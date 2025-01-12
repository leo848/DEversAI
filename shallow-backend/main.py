from typing import Annotated, Tuple
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from functools import cache as memoize
import json

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
    allow_headers=["*"]
)

@memoize
def load_token_infos() -> dict[int, list[Tuple[str, str]]]:
    with open("assets/example_strings.json") as f:
        return json.load(f)

@app.get("/")
def root_route():
    return { "status": "OK" }

@app.get("/v0/token/{token_id}/info")
def get_token_examples(token_id: int, token_examples: Annotated[dict, Depends(load_token_infos)]):
    examples = token_examples.get(str(token_id))
    if examples is None:
        raise HTTPException(status_code=400, detail="Invalid token_id")
    return { "id": token_id, "examples": token_examples[str(token_id)] }
