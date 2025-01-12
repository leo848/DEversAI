from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session
import json

DATABASE_URL = "sqlite:///assets/token_examples.db"

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
