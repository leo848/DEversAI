from typing import Literal, Optional, Union
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


class GeminiColumnRequest(BaseModel):
    path: list[str]


class BirthyearRequest(BaseModel):
    first_name: str
    last_name: str = "Müller"
    day: str = "20. September"


class BirthyearStats(BaseModel):
    mean: float
    std: float
    mode: float
    skew: float


class BirthyearResponse(BaseModel):
    year_data: dict[int, float]
    stats: BirthyearStats
    decade_results: dict[int, float]
    prob_sum: float
    discarded_prob_ratio: float

class ForcingRequest(BaseModel):
    token_input: list[int]

class ForcingAlternativeToken(BaseModel):
    token_id: int
    logit: float

class ForcingTokenStep(BaseModel):
    logit: float
    k: int
    alternatives: list[ForcingAlternativeToken]

class ForcingResponse(BaseModel):
    total_logprob: float
    steps: list[ForcingTokenStep]
