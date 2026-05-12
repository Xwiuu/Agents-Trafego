from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from domain.models import ChatMessage, AgentResponse

class LLMClient:
    def __init__(self, groq_api_key: str, model_name: str = "llama-3.1-8b-instant", temperature: float = 0.1):
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=model_name,
            temperature=temperature
        )
    
    def process_message(self, message: str) -> AgentResponse:
        """Processa uma mensagem usando o LLM e retorna uma resposta estruturada."""
        # Criar um prompt para o LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Você é um especialista em marketing digital. Analise a seguinte mensagem e forneça uma resposta útil."),
            ("user", "{input}")
        ])
        
        # Chamar o LLM
        response = self.llm.invoke(prompt.format_messages(input=message))
        
        # Retornar uma resposta estruturada
        return AgentResponse(
            response=response.content,
            metrics={
                "ctr": 0.0,
                "cpc": 0.0,
                "roas": 0.0
            }
        )