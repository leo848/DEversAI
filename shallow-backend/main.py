from fastapi import FastAPI, HTTPException, Depends, WebSocket
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session
import numpy as np
import json
import websockets
import requests
from models import LogitsRequest, RequestUnion, InferenceRequest
from validate import validate_model_name

DATABASE_URL = "sqlite:///assets/token_examples.db"
DEEP_URL_WS = "ws://127.0.0.1:8910/ws"
DEEP_URL_HTTP = "http://127.0.0.1:8910/"

engine: Engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, future=True
)

def get_db():
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:5173",
        "https://deversai.vercel.app",
        "http://deversai.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root_route():
    return {"status": "OK"}

@app.get("/v0/token/{token_id}/info")
def get_token_examples(token_id: int, db: scoped_session = Depends(get_db)):
    query = text("SELECT examples FROM token_examples WHERE token_id = :token_id")
    result = db.execute(query, {"token_id": str(token_id)}).fetchone()
    examples_idx = 0

    if not result:
        raise HTTPException(status_code=404, detail="Token ID not found")

    return {"id": token_id, "examples": json.loads(result[examples_idx])}

@app.get("/v0/tokens/{model_name}/embeddings")
def get_embeddings(model_name: str):
    validate_model_name(model_name)
    try:
        embeddings_3d = np.load(f"assets/embedding/3d/{model_name}.npy").tolist()
        embeddings_2d = np.load(f"assets/embedding/2d/{model_name}.npy").tolist()
        return {
            "tokenCount": len(embeddings_3d),
            "embeddings3D": embeddings_3d,
            "embeddings2D": embeddings_2d,
        }
    except IOError:
        raise HTTPException(404, "Model not found")

# Mapping from request_id -> client WebSocket
active_clients: dict[str, WebSocket] = {}

@app.websocket("/ws")
async def websocket_endpoint(client_ws: WebSocket):
    """Handles incoming WebSocket connections from clients."""
    await client_ws.accept()
    request_id = None  # Track the active request ID for cleanup
    
    try:
        while True:
            message = await client_ws.receive_text()
            data = json.loads(message)
            request = RequestUnion(**data)  # Auto-detect request type
            
            if isinstance(request, InferenceRequest):
                request_id = request.request_id
                active_clients[request_id] = client_ws  # Store client connection
                
                # Forward the request to Kira
                async with websockets.connect(DEEP_URL_WS) as kira_ws:
                    await kira_ws.send(message)

                    # Relay responses back to the correct client
                    async for response_text in kira_ws:
                        response = json.loads(response_text)
                        if response.get("request_id") == request_id:
                            await client_ws.send_text(response_text)

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if request_id and request_id in active_clients:
            del active_clients[request_id]  # Cleanup

@app.post("/v0/model/{model_name}/logits")
async def model_logits(
    model_name: str,
    request: LogitsRequest
):
    
    return requests.post(
        DEEP_URL_HTTP + "/model/" + model_name + "/logits",
        json=jsonable_encoder(request)
    ).json()
