from typing import Literal, Union
from pydantic import BaseModel

class BaseRequest(BaseModel):
    type: str
    request_id: str


class InferenceRequest(BaseRequest):
    type: Literal["autoregressiveInference"]
    model_id: str
    token_input: list[int]

class DistributionRequest(BaseRequest):
    type: Literal["distributionInference"]
    model_id: str
    token_input: list[int]

RequestUnion = Union[InferenceRequest, DistributionRequest]

class InferenceResponse(BaseModel):
    type: Literal["autoregressiveInference"]
    request_id: str
    tokens: list[int]
