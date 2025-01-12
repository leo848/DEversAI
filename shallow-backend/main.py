from contextlib import asynccontextmanager
from typing import Annotated, Tuple
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from functools import cache as memoize
import json

token_infos = {}

@asynccontextmanager
async def lifespan(_: FastAPI):
    with open("assets/example_strings.json") as f:
        token_infos["value"] = json.load(f)
    yield
    token_infos.clear()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:5173",
        "https://deversai.vercel.app",
        "http://deversai.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root_route():
    return { "status": "OK" }

@app.get("/v0/token/{token_id}/info")
def get_token_examples(token_id: int):
    examples = token_infos["value"].get(str(token_id))
    if examples is None:
        raise HTTPException(status_code=400, detail="Invalid token_id")
    return { "id": token_id, "examples": examples[str(token_id)] }
