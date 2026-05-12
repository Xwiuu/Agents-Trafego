from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import asyncio

app = FastAPI()

class ChatMessage(BaseModel):
    message: str
    sender: str  # 'user' or 'system'

class AgentResponse(BaseModel):
    response: str
    metrics: Dict[str, float]

# Simulação de processamento do LangGraph
async def process_with_langgraph(message: str) -> AgentResponse:
    # Simular processamento
    await asyncio.sleep(1)
    
    # Retornar resposta simulada
    return AgentResponse(
        response=f"Resposta processada para: {message}",
        metrics={
            "ctr": 3.25,
            "cpc": 12.40,
            "roas": 4.2
        }
    )

@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(message: ChatMessage):
    """
    Endpoint para enviar mensagens ao sistema LangGraph
    
    Args:
        message: Mensagem do usuário ou comando
        
    Returns:
        Resposta do sistema com métricas
    """
    if not message.message.strip():
        raise HTTPException(status_code=400, detail="Mensagem não pode ser vazia")
    
    try:
        response = await process_with_langgraph(message.message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}