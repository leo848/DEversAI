"""
Sample from a trained model
"""
import os
from tqdm import tqdm
from ast import literal_eval
import torch
import random
import json
from gpt import GPT
from vocabulary import Vocabulary
from torch.nn import functional as F

# -----------------------------------------------------------------------------
model_name = "causal-fw2-plenar1.pt"
vocab_file = "fineweb2.vocab"

compile = False # use PyTorch 2.0 to compile the model to be faster
causality = "anticausal" if "anticausal" in model_name else "causal" # 'causal' or 'anticausal'

# modes
show_probs = False
show_probs_tries = 1

show_token_generation_probs = False

show_samples_json = True

# config

num_samples = 128 # number of samples to draw
max_new_tokens = int(150) # number of tokens generated in each sample
temperature = 0.7 # 1.0 = no change, < 1.0 = less random, > 1.0 = more random, in predictions
top_k = 200 # retain only the top_k most likely tokens, clamp others to have 0 probability

seed = random.randint(0, int(1e10))
print(f"Using seed {seed}")
device = 'cuda' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.


exec(open('configurator.py').read()) # overrides from command line or config file
# -----------------------------------------------------------------------------

torch.manual_seed(seed)
torch.cuda.manual_seed(seed)

model = GPT.load(os.path.join("output", model_name))

if compile:
    model = torch.compile(model) # requires PyTorch 2.0 (optional)

vocab = Vocabulary.load(vocab_file)

# encode the beginning of the prompt
prompt_input = True
while prompt_input:
    raw_input = input("\n\x1B[32m>>> \x1B[0m")
    add_eot = "EOT" in raw_input
    raw_input = raw_input.replace("EOT", "")
    eval_input = literal_eval(f'"{raw_input}"')
    if causality == "causal":
        prompt_input = eval_input
    else:
        prompt_input = eval_input
    start_ids = vocab.encode(prompt_input, reverse=causality == "anticausal", add_eot=add_eot)

    x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])

    # run generation
    with torch.no_grad():
        if show_probs:
            if show_probs_tries == 1:
                logits, loss = model(x)
                logits = logits[:, -1, :] / temperature
                probs = F.softmax(logits, dim=-1)
                v, i = torch.topk(probs, 20)
                for prob, token_id in zip(v[0], i[0]):
                    print(f"{prob:.3f} {vocab.decode([int(token_id)])}")
            else:
                token_tries = [(x[0].tolist(), 1.0)]
                done = []
                while token_tries:
                    (cur_x, cur_prob) = token_tries[0]
                    token_tries = token_tries[1:]

                    if cur_prob < 0.0001:
                        continue

                    if len(cur_x) >= len(x[0]) + show_probs_tries:
                        done.append((cur_x, cur_prob))
                        continue

                    logits, loss = model(
                        torch.tensor(cur_x, dtype=torch.long, device=device)[None, ...]
                    )
                    logits = logits[:, -1, :] / temperature
                    probs = F.softmax(logits, dim=-1)
                    v, i = torch.topk(probs, 3)
                    for prob, token_id in zip(v[0][0], i[0][0]):
                        token_tries.append((cur_x + [int(token_id)], float(prob) * cur_prob))
                for (tokens, prob) in sorted(done, key=lambda p: -p[1]):
                    decoded = vocab.decode(tokens, reverse=causality=="anticausal")
                    print(f"{prob:.3f} {decoded}")
        elif show_token_generation_probs:
            idx = x
            res = []
            for _ in range(max_new_tokens):
                logits, _ = model(idx)
                logits = logits[:, -1, :] / temperature
                if top_k is not None:
                    v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                    logits[logits < v[:, [-1]]] = -float('Inf')
                probs = F.softmax(logits, dim=-1)
                idx_next = torch.multinomial(probs, num_samples=1)
                prob = probs[0][idx_next]
                res.append((float(prob), idx_next[0]))
                idx = torch.cat((idx, idx_next), dim=1)
            idx = idx[0][len(x):].tolist()
            print()
            for prob, token_id in res:
                print(f"{prob:.3f}", vocab.decode([int(token_id)]).replace("\n", "␤").replace(" ", "⎵"))
            print()
            print(vocab.decode(list(token_id for (_, token_id) in res), reverse=causality == "anticausal"), end="")
        elif show_samples_json:
            results = []
            try:
                for _ in tqdm(range(0, num_samples, 32)):
                    x = torch.tensor([x[0].tolist()] * 32, dtype=torch.long, device=device)
                    gen = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
                    for item in gen:
                        results.append(vocab.decode(item, reverse = causality == "anticausal" ))
            finally:
                with open("/tmp/show_samples-2.json", "w") as f:
                    json.dump(results, f)

        elif causality == 'causal':
            gen = model.generate_generator(x, max_new_tokens, temperature=temperature, top_k=top_k)
            print()
            print(prompt_input, end="", flush=True)
            colored = False
            COLORS = ["168;213;226", "248;191;213", "251;231;161", "178;226;180"]
            current_color = 0
            try:
                for token in gen:
                    token_bytes = vocab.decode_bytes(
                        token.tolist()[0]
                    )
                    if colored:
                        sys.stdout.buffer.write(f"\x1B[30;48;2;{COLORS[current_color]}m".encode())
                    sys.stdout.buffer.write(token_bytes)
                    if colored:
                        sys.stdout.buffer.write(f"\x1B[0m".encode())
                        current_color += 1
                        if current_color == len(COLORS):
                            current_color = 0
                    sys.stdout.flush()
            except KeyboardInterrupt:
                continue
            print()
        # elif causality == 'anticausal':
        #     y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
        #     string = vocab.decode(y[0], reverse=True)
        #     print(string + prompt_input)
        elif causality == 'anticausal':
            x_batch = torch.tensor([x[0].tolist()] * num_samples, dtype=torch.long, device=device)
            y_batch = model.generate(x_batch, max_new_tokens, temperature=temperature, top_k=top_k)
            for y in y_batch:
                string = vocab.decode(y, reverse=True)
                print("=" * 50)
                print(string + prompt_input)
