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
from infrastructure.api_clients.meta_ads_client import MetaAdsClient
from infrastructure.logger import global_logs
from infrastructure.vector_store import VectorStore

app = FastAPI(title="Meta Ads Agent API", version="2.0.0")

# Inicializa VectorStore para uso nas rotas
vector_store = VectorStore()
meta_client = MetaAdsClient()

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


@app.get("/api/metrics")
async def get_metrics():
    """
    Retorna métricas agregadas da Meta Ads para o dashboard sem passar pelo LLM.
    """
    try:
        campaigns = meta_client.get_campaign_performance_summaries(limit=50, date_preset="last_7d")
        total_spend = sum(float(c.get("spend") or 0) for c in campaigns)
        total_conversions = sum(int(c.get("conversions") or 0) for c in campaigns)
        weighted_roas_value = sum(float(c.get("spend") or 0) * float(c.get("roas") or 0) for c in campaigns)
        overall_roas = weighted_roas_value / total_spend if total_spend else 0.0
        average_cpa = total_spend / total_conversions if total_conversions else None
        top_campaigns = sorted(
            campaigns,
            key=lambda campaign: float(campaign.get("spend") or 0),
            reverse=True
        )[:10]

        return {
            "date_preset": "last_7d",
            "totals": {
                "total_spend": round(total_spend, 2),
                "total_conversions": total_conversions,
                "average_cpa": round(average_cpa, 2) if average_cpa is not None else None,
                "overall_roas": round(overall_roas, 2),
            },
            "top_campaigns": top_campaigns,
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar métricas Meta: {str(e)}")


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
