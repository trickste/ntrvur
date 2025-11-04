from pydantic.v1 import BaseModel, Field
from typing import List, Dict

class EvaluateResponse(BaseModel):
    payload: dict 

class EvaluateParams(BaseModel):
    candidate_name: str | None = None
    years_of_experience: int = Field(default=3, ge=0, le=50)
