from typing import Literal, Union
from pydantic import BaseModel, Field

class BaseRequest(BaseModel):
    request_id: str

class InferenceConfig(BaseModel):
    num_tokens: int = Field(default=200)
    temperature: float = Field(default=0.8)
    top_k: int = Field(default=200)
    synthetic_wait: float = Field(default=0.0)

class InferenceRequest(BaseModel):
    type: Literal["autoregressiveInference"]
    model_id: str
    token_input: list[int]
    config: InferenceConfig

class DistributionRequest(BaseModel):
    type: Literal["distributionInference"]
    model_id: str
    token_input: list[int]

class RequestUnion(BaseRequest):
    action: Union[InferenceRequest, DistributionRequest] = Field(discriminator="type")

class InferenceResponse(BaseModel):
    type: Literal["autoregressiveInference"]
    request_id: str
    tokens: list[int]
    done: bool = False

class LogitsRequest(BaseModel):
    token_input: list[int]

class LogitsResponse(BaseModel):
    logits: list[float]
