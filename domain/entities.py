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
    
    def __init__(self, id: str, name: str, platform: PlatformEnum, status: str, budget: float, metrics: Dict[str, float]):
        self.id = id
        self.name = name
        self.platform = platform
        self.status = status
        self.budget = budget
        self.metrics = metrics

@dataclass
class Metrics:
    ctr: float
    cpc: float
    roas: float
    conversions: int
    impressions: int
    clicks: int
    spend: float
    
    def __init__(self, ctr: float, cpc: float, roas: float, conversions: int, impressions: int, clicks: int, spend: float):
        self.ctr = ctr
        self.cpc = cpc
        self.roas = roas
        self.conversions = conversions
        self.impressions = impressions
        self.clicks = clicks
        self.spend = spend