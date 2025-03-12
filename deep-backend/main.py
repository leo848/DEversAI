from dataclasses import dataclass
from typing import Annotated
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.encoders import jsonable_encoder
import asyncio
from models import InferenceRequest, LogitsResponse, RequestUnion, InferenceResponse, LogitsRequest
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
]

# Load models and assign a unique CUDA Stream to each
MODELS = {}
STREAMS = {}

for model in MODEL_LOCATIONS:
    device = f"cuda:{model.cuda_gpu}"
    MODELS[model.name] = GPT.load(
        os.path.join("/output", model.name, f"ckpt_{model.ckpt}.pt"),
        device=device,
        compile=True,
    )
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

@app.post("/model/{model_id}/logits")
async def model_logits(model_id: str, request: LogitsRequest):
    if model_id not in MODELS:
        raise HTTPException(404, "Model not found")

    # Prepare input tensor
    idx = torch.tensor([request.token_input], dtype=torch.long)

    # Run inference asynchronously
    logits = await async_infer(model_id, idx)

    return LogitsResponse(logits=logits[0][0])  # Adjust indexing based on model output

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            request = RequestUnion(**data)

            if isinstance(request.action, InferenceRequest):
                test_tokens = [ 2574, 515, 383, 1187, 1826, 9553, 7092, 1269, 33 ]
                for token in test_tokens:
                    await websocket.send_json(
                        jsonable_encoder(
                            InferenceResponse(
                                type=request.action.type,
                                request_id=request.request_id,
                                tokens=[token],
                                done=False
                            )
                        )
                    )
                    await asyncio.sleep(0.2)
                await websocket.send_json(
                    jsonable_encoder(
                        InferenceResponse(
                            type=request.action.type,
                            request_id=request.request_id,
                            tokens=[],
                            done=True
                        )
                    )
                )
    except Exception as e:
        print(f"connection closed: {e}")
