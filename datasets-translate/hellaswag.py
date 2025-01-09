from typing import Literal
from tqdm import tqdm
from openai import OpenAI
import tiktoken
import os
import json
import random
from datasets import load_dataset

run_type: Literal["test"] | Literal["count_input_tokens"] | Literal["run_batch"] = "count_input_tokens"

client = OpenAI(
    # api_key="92130219"
        base_url="https://api.zukijourney.com/v1",
        api_key="zu-c4ca9126e8039773b099a8284445d7ea"
)

ds = load_dataset("Rowan/hellaswag")

system_prompt = """
You are designed to translate structured data. Your output must have exactly the same JSON keys as the input. You will translate from English to perfect, common and idiomatic German. s and comp must together form one congruent sentence. Output nothing but JSON.
""".strip()

def translation_task(datum):
    description = json.dumps({
        "s": datum["ctx"],
        "comp_0": datum["endings"][0],
        "comp_1": datum["endings"][1],
        "comp_2": datum["endings"][2],
        "comp_3": datum["endings"][3],
    })

    return {
        "custom_id": datum["ind"],
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "temperature": 0.1,
            "response_format": {
                "type": "json_object"
            },
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": description,
                }
            ]
        }
    }

def heading_print(string, n_eq=30):
    print()
    print("=" * n_eq, string.upper(), "=" * n_eq)

if __name__ == "__main__":
    os.makedirs("batches", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    batch_file_name = "batches/hellaswag.jsonl"
    batch_job_file_name = "batches/hellaswag.job"
    result_file_name = "output/hellaswag.jsonl"

    if run_type == "test":
        sample_datum = random.choice(ds["train"])
        heading_print("original")
        print(json.dumps(sample_datum, indent=4))
        print()

        task = translation_task(sample_datum)
        heading_print("request")
        print(json.dumps(task, indent=4))
        print()

        response = client.chat.completions.create(**task["body"])
        heading_print("response")
        print(response.choices[0].message.content)
        print()

        exit(0)
    elif run_type == "count_input_tokens":
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        input_cost_per_token = 0.075 / 1_000_000
        output_cost_per_token = 0.3 / 1_000_000
        total_cost = 0
        for key in ds:
            heading_print(f"Loading {key}")
            total_input_tokens = 0
            total_output_tokens = 0
            for datum in tqdm(ds[key]):
                messages = translation_task(datum)["body"]["messages"]
                input_strings = [m["content"] for m in messages]
                input_token_count = sum(len(encoding.encode(content)) for content in input_strings)
                GERMAN_HEURISTIC = 2.0
                output_token_count = int(len(encoding.encode(input_strings[1])) * GERMAN_HEURISTIC)
                total_input_tokens += input_token_count
                total_output_tokens += output_token_count
            print(f"{total_input_tokens} input tokens | {total_output_tokens} output tokens")
            input_cost = total_input_tokens * input_cost_per_token
            output_cost = total_output_tokens * output_cost_per_token
            total_cost += input_cost + output_cost
            print(f"{input_cost:.2}$ input cost | {output_cost:.2}$ output cost")
        heading_print("total cost")
        print(f"{total_cost:.2}$")
        exit(1)

    if os.path.exists(batch_job_file_name):
        print("Loading existing batch job")
        with open(batch_file_name) as file:
            batch_job = client.batches.retrieve(file.read())
        print("Status:", batch_job["status"])
        if batch_job["status"] == "completed":
            result_file_id = batch_job.output_file_id
            result = client.files.content(result_file_id).content

            with open(result_file_name, "wb") as file:
                file.write(result)

            print("Files extracted successfully")

        exit(0)

    tasks = []

    print("Accumulating tasks")
    for key in ds:
        for datum in ds[key]:
            tasks.append(translation_task(datum))

    print(" {len(tasks)} tasks")

    print()
    print("Writing tasks to .jsonl file")
    with open(batch_file_name, "w") as file:
        for task in tasks:
            file.write(json.dumps(task) + "\n")

    print(f"Uploading file {batch_file_name} to OpenAI")
    batch_file = client.files.create(
        file=open(batch_file_name, "rb"),
        purpose="batch"
    )

    print("Creating batch job")
    batch_job = client.batches.create(
        input_file_id=batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    print(f"Batch job created: {batch_job.id}")

    print(f"Saving batch job under {batch_job_file_name}")
    with open(batch_job_file_name, "w") as file:
        file.write(batch_job.id)

