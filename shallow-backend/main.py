import logging
from typing import cast
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session
import numpy as np
import json
import websockets
import requests
from models import GeminiColumnRequest, LogitsRequest, RequestUnion, InferenceRequest, BirthyearRequest
from vocabulary import Vocabulary
from validate import validate_model_name
from sklearn.neighbors import NearestNeighbors

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
logger = logging.getLogger("uvicon.error")

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

vocab = {
    "german-complete": Vocabulary.load("assets/german-complete.vocab"),
    "fineweb2": Vocabulary.load("assets/fineweb2.vocab"),
}


@app.get("/")
def root_route():
    return {"status": "OK"}

causal_fw2_embeddings = np.load("assets/embedding/768d/causal-fw2.npy")
anticausal_fw2_embeddings = np.load("assets/embedding/768d/anticausal-fw2.npy")

causal_fw2_nn_model = NearestNeighbors(metric = "cosine")
causal_fw2_nn_model.fit(causal_fw2_embeddings)
anticausal_fw2_nn_model = NearestNeighbors(metric = "cosine")
anticausal_fw2_nn_model.fit(anticausal_fw2_embeddings)

causal_fw2_cca = (causal_fw2_embeddings - np.mean(causal_fw2_embeddings)) @ np.load("assets/causal-fw2-wte-cca.npy").T
anticausal_fw2_cca = (anticausal_fw2_embeddings - np.mean(anticausal_fw2_embeddings)) @ np.load("assets/anticausal-fw2-wte-cca.npy").T

occurrences_direct = np.loadtxt("assets/direct_histogram2.txt", dtype=np.long)
occurrences_transitive = np.loadtxt("assets/transitive_histogram2.txt", dtype=np.long)

with open("assets/tokens-fw2-gemini.json") as f:
    gemini_fw2_tokens = json.load(f)

@app.get("/v0/token/{token_id}/info")
def token_info(token_id: int, db: scoped_session = Depends(get_db)):
    query = text("SELECT examples FROM token_examples_fineweb WHERE token_id = :token_id")
    result = db.execute(query, {"token_id": str(token_id)}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Token ID not found")

    (causal_fw2_nn_dist, causal_fw2_nn) = causal_fw2_nn_model.kneighbors([causal_fw2_embeddings[token_id]], 50)
    (anticausal_fw2_nn_dist, anticausal_fw2_nn) = anticausal_fw2_nn_model.kneighbors([anticausal_fw2_embeddings[token_id]], 50)

    occurrence_dict = {}
    occurrence_dict[str(token_id)] = {
        "count_direct": occurrences_direct[token_id].item(),
        "count_transitive": occurrences_transitive[token_id].item(),
    }
    for children in vocab["fineweb2"].tokens[token_id].children:
        for child in children:
            occurrence_dict[str(child.id())] = {
                "count_direct": occurrences_direct[child.id()].item(),
                "count_transitive": occurrences_transitive[child.id()].item(),
            }

    return {
        "id": token_id,
        "examples": json.loads(result[0]),
        "embedding_768d": {
            "causal_fw2": causal_fw2_embeddings[token_id].tolist(),
            "anticausal_fw2": anticausal_fw2_embeddings[token_id].tolist(),
        },
        "cca_embedding_768d": {
            "causal_fw2": causal_fw2_cca[token_id].tolist(),
            "anticausal_fw2": anticausal_fw2_cca[token_id].tolist(),
        },
        "occurrences": {
            "total": np.sum(occurrences_direct).item(),
            "tokens": occurrence_dict,
        },
        "nearest_neighbors": {
            "causal_fw2": {
                "neighbors": causal_fw2_nn[0][1:].tolist(),
                "distances": causal_fw2_nn_dist[0][1:].tolist(),
            },
            "anticausal_fw2": {
                "neighbors": anticausal_fw2_nn[0][1:].tolist(),
                "distances": anticausal_fw2_nn_dist[0][1:].tolist(),
            }
        },
        "gemini_info": gemini_fw2_tokens[token_id],
    }

@app.post("/v0/gemini-column")
def gemini_column(request: GeminiColumnRequest):
    EMPTY = {}
    result: list[str | int] = [-1] * 50256
    for entry in gemini_fw2_tokens:
        token_id = entry["id"]
        path = [*request.path]
        while path:
            if not isinstance(entry, (dict, list)):
                break
            first = path[0]
            path = path[1:]
            entry = entry.get(first, EMPTY)
            if entry == EMPTY:
                break
            if isinstance(entry, bool):
                entry = "ja" if entry else "nein"
        if entry == EMPTY:
            result[token_id] = -1
        else:
            result[token_id] = cast( str | int, entry)
    return {
        "column": result
    }

@app.get("/v0/embedding/{model_name}/{dim}/info")
def embedding_dim_info(model_name: str, dim: int):
    validate_model_name(model_name)
    if dim < 0 or dim >= 768:
        raise HTTPException(404, "Dim not found")
    embeddings = np.load(f"assets/embedding/768d/{model_name}.npy")
    return {
        "dim": dim,
        "token_values": embeddings[:, dim].tolist(),
    }


@app.get("/v0/cca-embedding/{dim}/info")
def cca_embedding_dim_info(dim: int):
    if dim < 0 or dim >= 768:
        raise HTTPException(404, "Dim not found")
    return {
        "dim": dim,
        "token_values": causal_fw2_cca[:, dim].tolist()
    }

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

            if isinstance(request.action, InferenceRequest):
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
            else:
                raise Exception(f"Unknown request: {request}")
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
        raise
    finally:
        if request_id and request_id in active_clients:
            del active_clients[request_id]  # Cleanup


@app.post("/v0/model/{model_name}/logits")
async def model_logits(model_name: str, request: LogitsRequest):

    return requests.post(
        DEEP_URL_HTTP + "/model/" + model_name + "/logits",
        json=jsonable_encoder(request),
    ).json()

@app.post("/v0/birthyear")
async def birthyear(request: BirthyearRequest):
    return requests.post(DEEP_URL_HTTP + "/birthyear", json=jsonable_encoder(request)).json()
