from fastapi import HTTPException

def validate_model_name(model_name: str):
    for letter in model_name:
        if not (letter.isalnum() or letter == "-"):
            raise HTTPException(401, f"Model name must be alphanumeric, contains {letter}")
