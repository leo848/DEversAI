from dataclasses import dataclass
from typing import Annotated
from fastapi import FastAPI, WebSocket
import asyncio
from models import InferenceRequest, RequestUnion, InferenceResponse, LogitsRequest

@dataclass
class ModelLocation:
    name: str
    ckpt: int
    cuda_gpu: int

MODEL_LOCATIONS = [
    ModelLocation("anticausal1", 300_000, 9),
    ModelLocation("causal1", 300_000, 9),
]

app = FastAPI()

@app.get("/")
async def root():
    return { "message": "Hello, world!" }

@app.post("/model/{model_id}/logits")
async def model_logits(
    model_id: str,
    request: LogitsRequest,
):
    pass


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
                    await websocket.send_json(InferenceResponse(type=request.action.type, request_id=request.request_id, tokens=[token]))
                    await asyncio.sleep(0.2)
    except Exception as e:
        print(f"connection closed: {e}")
