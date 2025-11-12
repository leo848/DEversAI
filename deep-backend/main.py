from dataclasses import dataclass
import heapq
import datetime
from math import inf
import math
from collections import defaultdict
import numpy as np
from torch.nn import functional as F
import re
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.encoders import jsonable_encoder
import asyncio
from models import (
    BirthyearRequest,
    BirthyearResponse,
    InferenceRequest,
    LogitsResponse,
    RequestUnion,
    InferenceResponse,
    LogitsRequest,
    BirthyearStats,
    ForcedTokenStep,
    ForcedAlternativeToken,
    ForcedSequenceRequest,
    ForcedSequenceResponse
)
from vocabulary import Vocabulary
from gpt import GPT
import os
import torch


@dataclass
class ModelLocation:
    name: str
    ckpt: int
    cuda_gpu: int


MODEL_LOCATIONS = [
    ModelLocation("anticausal1", 300_000, 9),
    ModelLocation("causal1", 300_000, 9),
    ModelLocation("anticausal-fw2", 300_000, 9),
    ModelLocation("causal-fw2", 300_000, 9),
    ModelLocation("anticausal-fw2-laws1", 301_000, 9),
    ModelLocation("causal-fw2-laws1", 301_000, 9),
    ModelLocation("anticausal-fw2-wikipedia1", 400_000, 9),
    ModelLocation("causal-fw2-wikipedia1", 400_000, 9),
    ModelLocation("anticausal-fw2-gutenberg1", 350_000, 9),
    ModelLocation("causal-fw2-gutenberg1", 350_000, 9),
    ModelLocation("anticausal-fw2-plenar1", 305_000, 9),
    ModelLocation("causal-fw2-plenar1", 305_000, 9),
]

# Load models and assign a unique CUDA Stream to each
MODELS = {}
STREAMS = {}

for model in MODEL_LOCATIONS:
    device = f"cuda:{model.cuda_gpu}"
    MODELS[model.name] = GPT.load(
        os.path.join("/output", model.name, f"ckpt_{model.ckpt}.pt"),
        device=device,
        compile=False,
    )
    MODELS[model.name].eval()
    STREAMS[model.name] = torch.cuda.Stream(device=torch.device(device))

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


async def async_infer(model_name: str, input_tensor):
    """Runs inference asynchronously using CUDA streams"""
    model = MODELS[model_name]
    stream = STREAMS[model_name]
    device = next(model.parameters()).device

    input_tensor = input_tensor.to(device)

    with torch.no_grad():
        with torch.cuda.stream(stream):
            logits, _ = model.forward(input_tensor)

    stream.synchronize()

    return logits.detach().cpu().numpy().tolist()

def analyze_logits_for_target(
    logits_vector: torch.Tensor, target_token_id: int
) -> ForcedTokenStep:
    log_probs = F.log_softmax(logits_vector, dim=-1)

    target_log_prob = log_probs[target_token_id].item()

    sorted_indices = torch.argsort(log_probs, descending=True)
    rank = (sorted_indices == target_token_id).nonzero(as_tuple=True)[0].item()

    top_log_probs, top_token_ids = torch.topk(log_probs, 100)

    alternatives = [
        ForcedAlternativeToken(token_id=token_id.item(), logit=log_prob.item())
        for token_id, log_prob in zip(top_token_ids, top_log_probs)
    ]

    return ForcedTokenStep(
        logit=target_log_prob,
        k=rank,
        alternatives=alternatives
    )

@app.post("/model/{model_id}/logits")
async def model_logits(model_id: str, request: LogitsRequest) -> LogitsResponse:
    if model_id not in MODELS:
        raise HTTPException(404, "Model not found")

    # Prepare input tensor
    idx = torch.tensor([request.token_input], dtype=torch.long)

    # Run inference asynchronously
    logits = await async_infer(model_id, idx)

    return LogitsResponse(logits=logits[0][0])  # Adjust indexing based on model output

@app.post("/model/{model_id}/forcing")
async def forcing(model_id: str, request: ForcedSequenceRequest) -> ForcedSequenceResponse:
    if model_id not in MODELS:
        raise HTTPException(status_code=404, detail="Model not found")

    if not request.token_input:
        raise HTTPException(status_code=400, detail="token_ids cannot be empty.")

    total_logprob = 0.0
    step_results = []

    # 1. Handle the first token from an empty context
    empty_context_tensor = torch.tensor([[]], dtype=torch.long)
    logits_np_first = await async_infer(model_id, empty_context_tensor)
    logits_first = torch.from_numpy(np.array(logits_np_first)).squeeze(0)

    first_step_result = analyze_logits_for_target(logits_first, request.token_input[0])
    step_results.append(first_step_result)
    total_logprob += first_step_result.logit

    # 2. Handle the rest of the tokens in a single batch, if they exist
    if len(request.token_input) > 1:
        rest_context_tensor = torch.tensor([request.token_input[:-1]], dtype=torch.long)
        logits_np_rest = await async_infer(model_id, rest_context_tensor)
        logits_rest = torch.from_numpy(np.array(logits_np_rest)).squeeze(0)

        # Ensure tensor is 2D for single-step context
        if logits_rest.dim() == 1:
            logits_rest = logits_rest.unsqueeze(0)

        for i in range(logits_rest.shape[0]):
            target_token_id = request.token_input[i + 1]
            step_result = analyze_logits_for_target(logits_rest[i], target_token_id)
            step_results.append(step_result)
            total_logprob += step_result.logit

    return ForcedSequenceResponse(
        total_logprob=total_logprob,
        steps=step_results
    )

@app.post("/birthyear")
async def birthyear(request: BirthyearRequest) -> BirthyearResponse:
    INCLUDE_EXPR = re.compile(r"^[0-9]+ ?")
    COMPLETE_YEAR = re.compile(r"^[0-9]{4}")
    NECESSARY_EXPR = re.compile(r"^[0-9]{0,3}$")

    vocab = Vocabulary.load("fineweb2.vocab")
    model_id = "causal-fw2-wikipedia1"
    if model_id not in MODELS:
        raise HTTPException(404, "Model not found")
    model = MODELS[model_id]
    device = next(model.parameters()).device

    token_mask = torch.zeros(50304, device=device)
    for token in range(50256):
        string = vocab.decode([token])
        if not re.match(INCLUDE_EXPR, string):
            token_mask[token] = -float("inf")

    continuations = [(-0.0, ())]

    results = defaultdict(float)

    # Verworfene Wahrscheinlichkeitsmasse
    total_discarded_prob_mass = 0.0

    while continuations:
        neg_log_prob, tokens = heapq.heappop(continuations)
        log_prob = -neg_log_prob
        if log_prob < math.log(1e-4):
            continue
        string = vocab.decode(list(tokens))
        input_string = f"# {request.first_name} {request.last_name}\n\n{request.first_name} {request.last_name} (* {request.day} {string}"
        if re.match(COMPLETE_YEAR, string):
            year = int(string[:4])
            results[year] += math.exp(log_prob)
        if not re.match(NECESSARY_EXPR, string):
            continue

        model_x = torch.tensor([vocab.encode(input_string)], device=device)
        model_y, _ = model(model_x)

        # Berechnung der Konfidenz ohne Tokenmaske
        with torch.no_grad():
            current_path_prob = math.exp(log_prob)
            next_token_probs = F.softmax(model_y[0][0], dim=-1)
            is_masked = token_mask == -inf
            discarded_mass_step = torch.sum(next_token_probs[is_masked]).item()
            total_discarded_prob_mass += current_path_prob * discarded_mass_step

        probs = F.log_softmax(model_y[0][0] + token_mask, dim=-1)
        top_probs, top_tokens = torch.topk(probs, 100)
        for token, token_log_prob in zip(top_tokens, top_probs):
            heapq.heappush(continuations, (-(log_prob + token_log_prob.item()), tokens + (int(token.item()),)))

    prob_sum = sum(results.values())
    results = {year: prob / prob_sum for year, prob in results.items()}
    decade_results = defaultdict(float)
    for year, prob in results.items():
        decade_results[year // 10 * 10] += prob

    keys = np.array(list(results.keys()))
    values = np.array(list(results.values()))
    stats_mean = np.average(keys, weights=values)
    stats_variance = np.average((keys - stats_mean) ** 2, weights=values)
    stats_std = np.sqrt(stats_variance)
    stats_mode = keys[np.argmax(values)]
    stats_third_moment = np.average((keys - stats_mean) ** 3, weights=values)
    stats_skew = stats_third_moment / stats_std**3

    stats = BirthyearStats(
        mean=float(stats_mean),
        std=float(stats_std),
        mode=float(stats_mode),
        skew=float(stats_skew),
    )

    total_explored_prob = prob_sum + total_discarded_prob_mass
    if total_explored_prob > 1e-6:
        discarded_prob_ratio = total_discarded_prob_mass / total_explored_prob
    else:
        discarded_prob_ratio = 0.0

    return BirthyearResponse(
        year_data=results,
        decade_results=decade_results,
        stats=stats,
        prob_sum=prob_sum,
        discarded_prob_ratio=discarded_prob_ratio
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            request = RequestUnion(**data)

            if isinstance(request.action, InferenceRequest):
                if request.action.model_id not in MODELS:
                    raise HTTPException(404, "Model not found")

                model = MODELS[request.action.model_id]
                stream = STREAMS[request.action.model_id]
                device = next(model.parameters()).device

                input_tensor = torch.tensor([request.action.token_input]).to(device)

                with torch.no_grad(), torch.cuda.stream(stream):
                    rest_tokens = []
                    last_send = datetime.datetime.now()
                    for token in model.generate_generator(
                        input_tensor,
                        max_new_tokens=request.action.config.num_tokens,
                        temperature=request.action.config.temperature,
                        top_k=request.action.config.top_k,
                    ):
                        rest_tokens.append(token)
                        await asyncio.sleep(request.action.config.synthetic_wait)
                        if datetime.datetime.now() - last_send >= datetime.timedelta(
                            seconds=0.1
                        ):
                            await websocket.send_json(
                                jsonable_encoder(
                                    InferenceResponse(
                                        type=request.action.type,
                                        request_id=request.request_id,
                                        tokens=rest_tokens,
                                        done=False,
                                    )
                                )
                            )
                            last_send = datetime.datetime.now()
                            rest_tokens = []
                await websocket.send_json(
                    jsonable_encoder(
                        InferenceResponse(
                            type=request.action.type,
                            request_id=request.request_id,
                            tokens=rest_tokens,
                            done=True,
                        )
                    )
                )
    except Exception as e:
        print(f"connection closed: {e}")
