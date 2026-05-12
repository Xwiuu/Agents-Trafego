from domain.models import ChatMessage, AgentResponse
from application.use_cases.process_message import process_message
from application.use_cases.route_message import route_message

# Implementação da lógica de roteamento de mensagens
def route_message(message: ChatMessage):
    # Esta função seria chamada quando uma nova mensagem é recebida
    # Ela determina qual agente deve lidar com a mensagem
    pass

def process_message(message: str):
    # Processa a mensagem usando o LangGraph
    # Esta função integraria com o LangGraph do seu código existente
    pass