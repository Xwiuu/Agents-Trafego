from typing import Dict, List
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    message: str
    sender: str = Field(default='user')

class AgentResponse(BaseModel):
    response: str
    metrics: Dict[str, float]