import os
import sys
from dotenv import load_dotenv

# Forçar recarregamento das variáveis de ambiente
load_dotenv(override=True)

# Garante que o diretório raiz está no path para evitar ModuleNotFoundError
sys.path.append(os.getcwd())

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from interfaces.routes import app as routes_app
from application.use_cases.autonomous_routine import run_autonomous_inspection
from infrastructure.logger import global_logs, logger

# Configuração do Motor de Agendamento
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    # TODO: Mudar para 4 horas em produção
    scheduler.add_job(run_autonomous_inspection, "interval", minutes=5)
    scheduler.start()
    logger.info("⏰ [Turno da Madrugada] Scheduler iniciado. Próxima inspeção agendada.")
    
    yield
    
    # --- SHUTDOWN ---
    logger.info("🛑 [System] Iniciando desligamento seguro...")
    scheduler.shutdown()
    logger.info("✅ [System] Scheduler desligado com sucesso.")

# Inicializa o app principal unificando as rotas e o ciclo de vida
app = routes_app
app.router.lifespan_context = lifespan

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Tratador global de exceções para garantir que qualquer erro crítico 
    seja logado e retorne um JSON padronizado ao invés de HTML.
    """
    logger.exception(f"Erro não tratado na rota {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Erro interno do servidor",
            "details": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando Servidor API Missão Crítica...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
