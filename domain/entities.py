from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .enums import PlatformEnum

@dataclass
class Campaign:
    id: str
    name: str
    platform: PlatformEnum
    status: str
    budget: float
    metrics: Dict[str, float]

@dataclass
class Metrics:
    ctr: float
    cpc: float
    roas: float
    conversions: int
    impressions: int
    clicks: int
    spend: float