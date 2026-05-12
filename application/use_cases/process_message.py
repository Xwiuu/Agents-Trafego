import os
from domain.models import ChatMessage, AgentResponse
from application.use_cases.orchestrator import RouterSystem
from dotenv import load_dotenv

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

        return AgentResponse(
            response=response_text,
            metrics={
                "ctr": 3.25,
                "cpc": 12.40,
                "roas": 4.2
            }
        )
    except Exception as e:
        return AgentResponse(
            response=f"❌ [Erro] Falha ao processar mensagem: {str(e)}",
            metrics={"ctr": 0, "cpc": 0, "roas": 0}
        )