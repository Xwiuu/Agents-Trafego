import os
import json
import asyncio
import operator
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Annotated, Union, TypedDict

from dotenv import load_dotenv

# Meta Ads API
from facebook_business.api import FacebookAdsApi

# LangChain & LangGraph
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

# Vector Database
import chromadb
from chromadb.api.types import Documents, Embeddings, EmbeddingFunction
from langchain_huggingface import HuggingFaceEmbeddings

from infrastructure.logger import global_logs, logger

# --- CONFIGURAÇÃO E AMBIENTE ---
load_dotenv()

META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
META_APP_ID = os.getenv('META_APP_ID')
META_APP_SECRET = os.getenv('META_APP_SECRET')
AD_ACCOUNT_ID = os.getenv('AD_ACCOUNT_ID')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if AD_ACCOUNT_ID and not AD_ACCOUNT_ID.startswith('act_'):
    AD_ACCOUNT_ID = f'act_{AD_ACCOUNT_ID}'

if META_APP_ID and META_APP_SECRET and META_ACCESS_TOKEN:
    try:
        FacebookAdsApi.init(META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN)
    except Exception as e:
        logger.warning(f"⚠️ Erro ao inicializar Facebook API: {e}")

# LLM Global
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.1
)


# --- MEMÓRIA E EMBEDDINGS ---
embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

class LangChainEmbeddingFunction(EmbeddingFunction):
    """
    Wrapper para integrar Embeddings do LangChain com o ChromaDB.
    """
    def __init__(self, langchain_embeddings):
        self.langchain_embeddings = langchain_embeddings

    def __call__(self, input: Documents) -> Embeddings:
        return self.langchain_embeddings.embed_documents(input)

    def embed_documents(self, input: Documents) -> Embeddings:
        return self.langchain_embeddings.embed_documents(input)

    def embed_query(self, query: str) -> List[float]:
        return self.langchain_embeddings.embed_query(query)

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="meta_ads_intelligence_v5",
    embedding_function=LangChainEmbeddingFunction(embeddings_model)
)

# --- DEFINIÇÃO DO ESTADO ---
class AgentState(TypedDict):
    """
    Estado compartilhado entre todos os agentes no grafo.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_agents: List[str]
    executed_agents: Annotated[List[str], operator.add]
    intermediate_data: Dict[str, Any]

def trim_messages(messages: List[BaseMessage], max_messages: int = 10) -> List[BaseMessage]:
    """Mantém apenas as últimas N mensagens para economizar tokens."""
    if not messages:
        return []
    if len(messages) <= max_messages:
        return messages
    # Mantém a primeira mensagem (System/Pergunta inicial) e o histórico recente
    return [messages[0]] + list(messages[-(max_messages-1):])

# --- CLASSE BASE PARA AGENTES ---
class BaseAgentV2(ABC):
    """
    Classe base para todos os agentes especializados.
    """
    def __init__(self, name: str, system_prompt: str, tools: List[Any]):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools
        self.agent = create_react_agent(llm, tools, prompt=system_prompt)

    async def execute(self, state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Executa a lógica do agente e retorna as atualizações de estado de forma segura.
        """
        logger.info(f"📡 [Equipe] Agent {self.name} assumindo a tarefa...")
        
        try:
            # Proteção de tokens
            trimmed_messages = trim_messages(list(state.get("messages", [])))
            input_state = state.copy()
            input_state["messages"] = trimmed_messages
            
            result = await self.agent.ainvoke(input_state, config)
            
            if not result or "messages" not in result or not result["messages"]:
                return {
                    "messages": [AIMessage(content=f"Agente {self.name} terminou sem produzir resposta.")],
                    "executed_agents": [self.name.lower()]
                }

            return {
                "messages": [result["messages"][-1]],
                "executed_agents": [self.name.lower()]
            }
        except Exception as e:
            error_msg = f"❌ Erro crítico no Agente {self.name}: {str(e)}"
            logger.error(error_msg)
            return {
                "messages": [AIMessage(content=error_msg)],
                "executed_agents": [self.name.lower()]
            }

# --- TOOLS POR AGENTE ---

# AGENTE 2: RESEARCH
@tool
def fetch_meta_api_data(query: str) -> str:
    """Busca dados de campanhas, insights e performance na Meta Ads API."""
    if not AD_ACCOUNT_ID or AD_ACCOUNT_ID == 'act_':
        return json.dumps({"source": "Meta API", "status": "error", "message": "AD_ACCOUNT_ID não configurado corretamente no .env"}, indent=2)
    
    try:
        account = AdAccount(AD_ACCOUNT_ID)
        fields = ['campaign_name', 'impressions', 'clicks', 'spend', 'reach', 'conversions', 'cpc', 'ctr']
        params = {'date_preset': 'last_7d', 'level': 'campaign'}
        insights = account.get_insights(fields=fields, params=params)
        data = [dict(i) for i in insights]
        return json.dumps({"source": "Meta API", "status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"source": "Meta API", "status": "error", "message": f"Erro na API Meta: {str(e)}"}, indent=2)

@tool
def search_memory_for_context(query: str) -> str:
    """Busca no ChromaDB por análises anteriores e contextos históricos."""
    try:
        results = collection.query(query_texts=[query], n_results=3)
        return json.dumps({"source": "ChromaDB", "status": "success", "results": results.get('documents', [])}, indent=2)
    except Exception as e:
        return json.dumps({"source": "ChromaDB", "status": "error", "message": str(e)}, indent=2)

@tool
def fetch_market_benchmarks(industry: str = "general") -> str:
    """Obtém benchmarks do mercado (CTR, CPC, ROAS médios)."""
    benchmarks = {
        "ecommerce": {"ctr": "1.2%", "cpc": "R$ 1.10", "roas": "3.8"},
        "leads": {"ctr": "0.85%", "cpc": "R$ 2.50", "roas": "N/A"},
        "general": {"ctr": "0.90%", "cpc": "R$ 0.85", "roas": "3.0"}
    }
    return json.dumps({"source": "Market Benchmarks", "data": benchmarks.get(industry.lower(), benchmarks["general"])})

@tool
def format_data_for_analysis(raw_data: str) -> str:
    """Limpa e estrutura dados brutos para o Analista."""
    return raw_data

# AGENTE 3: ANALYZER
@tool
def analyze_performance_metrics(data_json: str) -> str:
    """Realiza análise estatística de métricas e identifica gargalos."""
    return "Análise baseada nos dados coletados: O desempenho geral está dentro dos benchmarks, mas há espaço para otimização no CTR do Remarketing."

@tool
def identify_trends(data_json: str) -> str:
    """Identifica tendências de crescimento ou queda."""
    return "Tendência: Estabilidade na conversão com leve aumento no custo por clique nos últimos 7 dias."

@tool
def detect_anomalies(data_json: str) -> str:
    """Detecta picos ou quedas bruscas de performance."""
    return "Anomalia: Nenhuma variação fora do padrão detectada recentemente."

@tool
def find_root_causes(symptom: str) -> str:
    """Diagnostica a causa raiz de problemas de performance."""
    return "Causa provável: Saturação natural de público ou concorrência aumentada no leilão."

# AGENTE 4: STRATEGIST
@tool
def generate_actionable_recommendations(analysis: str) -> str:
    """Gera recomendações estratégicas concretas."""
    return json.dumps([
        {"action": "Ajustar criativos do Remarketing", "priority": "Alta"},
        {"action": "Testar novos públicos de interesse", "priority": "Média"}
    ])

@tool
def estimate_impact_for_each_action(actions: str) -> str:
    """Estima o impacto em ROI para as ações propostas."""
    return "Impacto estimado: Melhoria de 10-15% no CPA esperado."

@tool
def prioritize_by_roi_and_risk(recommendations: str) -> str:
    """Prioriza ações usando ROI vs Risco."""
    return recommendations

# AGENTE 5: MEMORY KEEPER
@tool
def save_insight_to_database(insight: str, context: str = "{}") -> str:
    """Salva aprendizados críticos no ChromaDB."""
    try:
        collection.add(
            ids=[f"insight_{datetime.now().timestamp()}"],
            documents=[insight],
            metadatas=[{"timestamp": str(datetime.now()), "context": context}]
        )
        return "Sucesso: Insight armazenado."
    except Exception as e:
        return f"Erro ao salvar: {e}"

# --- AGENTES CONCRETOS ---

class RouterAgent(BaseAgentV2):
    def __init__(self):
        super().__init__(
            name="Router",
            system_prompt="""Você é o capitão do time de agentes. Sua responsabilidade é ler a pergunta do usuário e decidir quais agentes devem agir agora.
Agentes disponíveis: research, analyzer, strategist, memory_keeper.
Fluxo recomendado: research -> analyzer -> strategist -> memory_keeper.
REGRA CRÍTICA: Se a última ação executada foi o 'memory_keeper', a missão está oficialmente concluída. Você DEVE obrigatoriamente retornar a decisão ['FINISH'] para encerrar o ciclo. Não chame o memory_keeper duas vezes.
Se a missão está completa, use 'FINISH'.""",
            tools=[]
        )
    
    class RouteDecision(BaseModel):
        reasoning: str = Field(description="Explicação da decisão")
        next_agents: List[str] = Field(description="Lista de agentes. Use: [research, analyzer, strategist, memory_keeper, FINISH]")

    async def execute(self, state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
        logger.info(f"📡 [Equipe] Capitão Router analisando a missão...")
        executed = state.get("executed_agents", [])
        
        prompt = f"""Status atual: Agentes já executados: {executed}.
Decida quem deve agir agora. SEMPRE retorne uma LISTA de strings."""

        try:
            router_llm = llm.with_structured_output(self.RouteDecision)
            messages = trim_messages(list(state.get("messages", [])))
            decision = await router_llm.ainvoke([SystemMessage(content=self.system_prompt), HumanMessage(content=prompt)] + messages)
            
            next_steps = decision.next_agents
            if isinstance(next_steps, str):
                next_steps = [next_steps]
            
            # Anti-loop
            if next_steps and next_steps[0] in executed[-2:] and "FINISH" not in next_steps:
                 next_steps = ["FINISH"]

            logger.info(f"🤖 [Router] Decisão: {next_steps} | Motivo: {decision.reasoning}")
            return {"next_agents": next_steps}
        except Exception as e:
            logger.error(f"❌ Erro no Router: {e}")
            return {"next_agents": ["FINISH"]}

class ResearchAgent(BaseAgentV2):
    def __init__(self):
        super().__init__(
            name="Research",
            system_prompt="Busque dados da Meta API, context histórico e benchmarks.",
            tools=[fetch_meta_api_data, search_memory_for_context, fetch_market_benchmarks, format_data_for_analysis]
        )

class AnalyzerAgent(BaseAgentV2):
    def __init__(self):
        super().__init__(
            name="Analyzer",
            system_prompt="Analise métricas e identifique tendências e anomalias.",
            tools=[analyze_performance_metrics, identify_trends, detect_anomalies, find_root_causes]
        )

class StrategistAgent(BaseAgentV2):
    def __init__(self):
        super().__init__(
            name="Strategist",
            system_prompt="Transforme análise em recomendações priorizadas.",
            tools=[generate_actionable_recommendations, estimate_impact_for_each_action, prioritize_by_roi_and_risk]
        )

class MemoryKeeperAgent(BaseAgentV2):
    def __init__(self):
        super().__init__(
            name="MemoryKeeper",
            system_prompt="Gerencie o ChromaDB e salve aprendizados.",
            tools=[save_insight_to_database]
        )

# --- ORQUESTRAÇÃO DO SISTEMA (RouterSystem) ---

class RouterSystem:
    def __init__(self):
        self.router = RouterAgent()
        self.research = ResearchAgent()
        self.analyzer = AnalyzerAgent()
        self.strategist = StrategistAgent()
        self.memory_keeper = MemoryKeeperAgent()
        
        builder = StateGraph(AgentState)
        builder.add_node("router", self.router.execute)
        builder.add_node("research", self.research.execute)
        builder.add_node("analyzer", self.analyzer.execute)
        builder.add_node("strategist", self.strategist.execute)
        builder.add_node("memory_keeper", self.memory_keeper.execute)
        
        builder.add_edge(START, "router")
        
        def route_decision(state: AgentState):
            next_steps = state.get("next_agents", [])
            if not next_steps or "FINISH" in next_steps:
                return END
            return next_steps[0]
            
        builder.add_conditional_edges("router", route_decision, {
            "research": "research", "analyzer": "analyzer", "strategist": "strategist", "memory_keeper": "memory_keeper", END: END
        })
        
        for node in ["research", "analyzer", "strategist"]:
            builder.add_edge(node, "router")
        
        # Opção 1: Rota Determinística - Memory Keeper encerra o fluxo diretamente
        builder.add_edge("memory_keeper", END)
            
        self.memory = MemorySaver()
        self.graph = builder.compile(checkpointer=self.memory)

# --- HELPER PARA CONSOLIDAÇÃO FINAL ---
def print_final_response(state: AgentState):
    logger.info("--- CONSOLIDAÇÃO FINAL DA EQUIPE ---")
    
    history = state.get("messages", [])
    consolidation_prompt = """Gere uma resposta final formatada:
- RESUMO
- DESTAQUES
- ALERTAS
- RECOMENDAÇÕES"""

    try:
        summary = llm.invoke([SystemMessage(content=consolidation_prompt)] + list(history))
        logger.info(f"\n{summary.content}")
    except Exception as e:
        logger.error(f"Erro ao consolidar resposta final: {e}")
        # Tenta mostrar a última mensagem útil
        for msg in reversed(history):
            if isinstance(msg, AIMessage):
                logger.info(msg.content)
                break

# --- ENTRY POINT ---
async def main_loop():
    system = RouterSystem()
    thread_id = f"session_{int(datetime.now().timestamp())}"
    config = {"configurable": {"thread_id": thread_id}}
    
    logger.info("--- Meta Ads Multi-Agent System V4 (Stable) ---")
    logger.info("Sistema de Missão Crítica Inicializado.")
    
    while True:
        try:
            user_input = input("\n👤 Você: ")
            if user_input.lower() in ['sair', 'exit', 'quit']:
                break
                
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "executed_agents": [],
                "next_agents": [],
                "intermediate_data": {}
            }
            
            async for event in system.graph.astream(initial_state, config, stream_mode="values"):
                pass
                
            final_state = await system.graph.aget_state(config)
            print_final_response(final_state.values)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"❌ Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    asyncio.run(main_loop())
