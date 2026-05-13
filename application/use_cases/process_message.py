import os
import re
from domain.models import ChatMessage, AgentResponse
from application.use_cases.orchestrator import RouterSystem
from dotenv import load_dotenv

def extract_metrics(text: str) -> dict:
    """Extrai métricas do texto usando Regex (Abordagem Avançada)."""
    metrics = {"ctr": 0.0, "cpc": 0.0, "roas": 0.0}

    # Regex para capturar números decimais ou inteiros após as palavras-chave
    ctr_match = re.search(r"ctr[:\s]+([\d,.]+)", text, re.IGNORECASE)
    cpc_match = re.search(r"cpc[:\s]+([\d,.]+)", text, re.IGNORECASE)
    roas_match = re.search(r"roas[:\s]+([\d,.]+)", text, re.IGNORECASE)

    if ctr_match:
        try: metrics["ctr"] = float(ctr_match.group(1).replace(",", ".").replace("%", ""))
        except: pass
    if cpc_match:
        try: metrics["cpc"] = float(cpc_match.group(1).replace(",", ".").replace("R$", ""))
        except: pass
    if roas_match:
        try: metrics["roas"] = float(roas_match.group(1).replace(",", "."))
        except: pass

    return metrics

async def process_message(message: ChatMessage) -> AgentResponse:
    """
    Processa uma mensagem usando o RouterSystem e retorna uma resposta estruturada.
    """
    # Recarregar .env para garantir que pegamos a chave atualizada do Vault
    load_dotenv(override=True)
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        return AgentResponse(
            response="⚠️ [Vault] Groq API Key não encontrada. Por favor, configure seu acesso no Vault.",
            metrics={"ctr": 0, "cpc": 0, "roas": 0}
        )

    try:
        orchestrator = RouterSystem(api_key=groq_api_key)
        response_text = await orchestrator.run(message.message)

        # Extrair métricas reais via Regex
        metrics = extract_metrics(response_text)

        return AgentResponse(
            response=response_text,
            metrics=metrics
        )
    except Exception as e:
        return AgentResponse(
            response=f"❌ [Erro] Falha ao processar mensagem: {str(e)}",
            metrics={"ctr": 0, "cpc": 0, "roas": 0}
        )