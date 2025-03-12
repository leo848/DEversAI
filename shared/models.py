from typing import Literal, Union
from pydantic import BaseModel, Field

class BaseRequest(BaseModel):
    request_id: str

class InferenceRequest(BaseModel):
    type: Literal["autoregressiveInference"]
    model_id: str
    token_input: list[int]

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

class LogitsRequest(BaseModel):
    token_input: list[int]

class LogitsResponse(BaseModel):
    logits: list[float]
