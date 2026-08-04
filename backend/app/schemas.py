from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class HealthCheck(BaseModel):
    status: str

class FineCreate(BaseModel):
    reason: str
    amount_aed: float

class AiSummaryRequest(BaseModel):
    site: str
    aqi: float
    noxKgDay: float
    pm25: float
    machines: list
    flaggedReplacements: int
