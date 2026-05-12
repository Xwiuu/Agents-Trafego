from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ChatMessage(BaseModel):
    message: str
    sender: str = Field(default='user')

class AgentResponse(BaseModel):
    response: str
    metrics: Dict[str, float]

# Não é necessário definir uma nova classe aqui, pois já temos o AgentResponse em domain/models.py
# Esta classe é apenas um exemplo de schema que poderia ser usado na API