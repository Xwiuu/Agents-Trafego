import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from application.use_cases.orchestrator import RouterSystem
from infrastructure.logger import global_logs, logger

# Import das ferramentas necessárias para o contexto da inspeção
from application.use_cases.tools.meta_tools import tool_get_active_campaigns, tool_get_campaign_metrics
from application.use_cases.tools.operator_tools import tool_pause_campaign
from application.use_cases.tools.memory_tools import tool_save_memory

AUDIT_FILE = "audit_logs.json"

def save_audit_log(action: str, campaign_id: str, reason: str):
    """Salva um registro de auditoria em arquivo JSON."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "campaign_id": campaign_id,
        "reason": reason
    }
    
    logs = []
    if os.path.exists(AUDIT_FILE):
        try:
            with open(AUDIT_FILE, "r") as f:
                logs = json.load(f)
        except:
            logs = []
            
    logs.append(log_entry)
    
    with open(AUDIT_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def get_daily_action_count() -> int:
    """Conta quantas ações foram realizadas hoje."""
    if not os.path.exists(AUDIT_FILE):
        return 0
    
    today = datetime.now().date().isoformat()
    try:
        with open(AUDIT_FILE, "r") as f:
            logs = json.load(f)
            return sum(1 for log in logs if log["timestamp"].startswith(today))
    except:
        return 0

async def run_autonomous_inspection():
    """
    Executa a rotina de inspeção autônoma das campanhas do Meta Ads com Guardrails.
    """
    logger.info("🤖 [Turno da Madrugada] Inspeção autônoma em andamento...")
    
    try:
        # Recarregar .env para garantir acesso às chaves do Vault
        load_dotenv(override=True)
        groq_api_key = os.getenv("GROQ_API_KEY")
        max_actions = int(os.getenv("MAX_DAILY_ACTIONS", "5"))

        if not groq_api_key:
            logger.error("⚠️ [Turno da Madrugada] Erro: GROQ_API_KEY não encontrada. Configure o Vault.")
            return

        # --- GUARDRAIL: Verificação de Teto de Segurança ---
        current_actions = get_daily_action_count()
        if current_actions >= max_actions:
            blocked_msg = f"⚠️ [Guardrail] Ação bloqueada pelo Teto de Segurança ({current_actions}/{max_actions} ações hoje)."
            logger.warning(blocked_msg)
            return

        # Prompt de Sistema oculto para o Orquestrador
        autonomous_prompt = (
            "Iniciando inspeção autônoma agendada. Analise todas as campanhas ativas. "
            "Se alguma campanha tiver um ROAS menor que 1.0 e um gasto superior a R$ 50,00, "
            "chame o Operator para PAUSAR a campanha imediatamente. "
            "Se houver campanhas com ROAS maior que 3.0, liste-as para futuro aumento de orçamento. "
            "Grave um resumo das suas ações na memória. "
            "IMPORTANTE: Sempre que pausar ou recomendar escala, descreva claramente o ID da campanha e o motivo."
        )

        # Instancia o orquestrador (LangGraph)
        orchestrator = RouterSystem(api_key=groq_api_key)
        
        # Executa a cadeia de agentes
        response = await orchestrator.run(autonomous_prompt)
        
        # --- PARSER DE AUDITORIA (Simulado por Regex simples para fins de POC) ---
        if "PAUSAR" in response or "pausada" in response.lower():
            save_audit_log("Pausa", "Detectado na Resposta", "ROAS Crítico (< 1.0)")
        elif "escala" in response.lower() or "aumentar" in response.lower():
            save_audit_log("Escala", "Detectado na Resposta", "ROAS Excelente (> 3.0)")
        
        logger.info("✅ [Turno da Madrugada] Ciclo de inspeção concluído.")
        
    except Exception as e:
        logger.exception(f"❌ [Turno da Madrugada] Falha crítica na rotina autônoma: {str(e)}")
