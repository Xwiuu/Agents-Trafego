from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Dict

# Inicializa ambiente
load_dotenv()

from domain.models import ChatMessage, AgentResponse
from application.use_cases.process_message import process_message
from application.use_cases.route_message import route_message
from interfaces.settings import router as settings_router
from infrastructure.logger import global_logs
from infrastructure.vector_store import VectorStore

app = FastAPI(title="Meta Ads Agent API", version="2.0.0")

# Inicializa VectorStore para uso nas rotas
vector_store = VectorStore()

# CORS para permitir requisições do Next.js (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar router do Settings Vault
app.include_router(settings_router)


import json
import os

@app.get("/api/audit-logs")
async def get_audit_logs():
    """
    Retorna os últimos 10 eventos de auditoria das ações autônomas.
    """
    audit_file = "audit_logs.json"
    if not os.path.exists(audit_file):
        return []
    
    try:
        with open(audit_file, "r") as f:
            logs = json.load(f)
            # Retorna os últimos 10 logs (mais recentes primeiro)
            return logs[-10:][::-1]
    except Exception as e:
        return []

@app.get("/api/logs")
async def get_system_logs():
    """
    Retorna os logs recentes do sistema para o Dashboard
    """
    return global_logs.get_logs()


@app.post("/api/memory/reset")
async def reset_memory():
    """
    Limpa toda a memória vetorial do ChromaDB
    """
    try:
        vector_store.clear_all_memory()
        global_logs.add_log("Memória Vetorial resetada pelo usuário.", "WARN")
        return {"status": "success", "message": "Memória limpa com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao resetar memória: {str(e)}")


@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(message: ChatMessage):
    """
    Endpoint para enviar mensagens ao sistema LangGraph
    """
    if not message.message.strip():
        raise HTTPException(status_code=400, detail="Mensagem não pode ser vazia")
    
    try:
        response = await process_message(message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/route", response_model=List[str])
async def route_endpoint(message: ChatMessage):
    """
    Endpoint para rotear mensagens para as plataformas apropriadas
    """
    try:
        platforms = route_message(message.message)
        return [p.value for p in platforms]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no roteamento: {str(e)}")