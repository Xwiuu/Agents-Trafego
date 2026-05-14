import os
import json
import asyncio
import operator
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Annotated, Union, TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
try:
    from groq import BadRequestError
except ImportError:  # pragma: no cover - protege ambientes sem o pacote Groq instalado
    BadRequestError = None

from domain.models import ChatMessage, AgentResponse

# Import das Ferramentas Reais
from application.use_cases.tools.meta_tools import tool_get_active_campaigns, tool_get_campaign_metrics, tool_get_campaigns
from application.use_cases.tools.memory_tools import tool_save_memory, tool_search_memory
from application.use_cases.tools.operator_tools import tool_pause_campaign, tool_increase_budget
from infrastructure.logger import global_logs, logger

DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"
ANALYZER_GROQ_MODEL = os.getenv("GROQ_ANALYZER_MODEL", DEFAULT_GROQ_MODEL)
MAX_CONTEXT_MESSAGES = 5
TOOL_VALIDATION_ERROR_MESSAGE = "Erro: Você tentou usar uma ferramenta que não possui. Use o fluxo correto de agentes."

READ_ONLY_META_TOOLS = [tool_get_campaigns, tool_get_active_campaigns, tool_get_campaign_metrics]
MUTATION_META_TOOLS = [tool_pause_campaign, tool_increase_budget]
OPERATOR_TOOLS = READ_ONLY_META_TOOLS + MUTATION_META_TOOLS

# --- ESTADO DO AGENTE ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_agents: List[str]
    executed_agents: Annotated[List[str], operator.add]
    intermediate_data: Dict[str, Any]

def trim_messages(messages: List[BaseMessage], max_messages: int = MAX_CONTEXT_MESSAGES) -> List[BaseMessage]:
    """Envia só as últimas mensagens ao LLM para caber no limite TPM da Groq."""
    if not messages:
        return []
    if len(messages) <= max_messages:
        return messages
    return list(messages[-max_messages:])

def is_tool_validation_bad_request(error: Exception) -> bool:
    """Identifica erros 400 de validação de tool vindos do provedor de LLM."""
    if BadRequestError is None or not isinstance(error, BadRequestError):
        return False

    error_text = str(error).lower()
    return any(marker in error_text for marker in (
        "tool_use_failed",
        "tool use failed",
        "tool call",
        "tools",
    ))

def should_retry_agent_error(error: Exception) -> bool:
    return not is_tool_validation_bad_request(error)

# --- ORQUESTRADOR ---
class RouterSystem:
    def __init__(self, api_key: Optional[str] = None):
        """O orquestrador agora carrega as chaves dinamicamente a cada execução."""
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _get_llm(self, model_name: Optional[str] = None):
        """Instancia o LLM com a chave atualizada do ambiente."""
        load_dotenv(override=True)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
             raise ValueError("⚠️ [Critical] GROQ_API_KEY não encontrada no ambiente.")
        
        return ChatGroq(
            groq_api_key=api_key,
            model_name=model_name or os.getenv("GROQ_DEFAULT_MODEL", DEFAULT_GROQ_MODEL),
            temperature=0.1
        )

    def _compact_state(self, state: AgentState) -> AgentState:
        compact_state = dict(state)
        compact_state["messages"] = trim_messages(list(state.get("messages", [])))
        return compact_state

    def _build_graph(self):
        builder = StateGraph(AgentState)
        
        # --- DEFINIÇÃO DOS NODES COM INSTANCIAÇÃO DINÂMICA ---
        
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception(should_retry_agent_error),
            reraise=True
        )
        async def research_node(state: AgentState, config: RunnableConfig):
            global_logs.set_active_agent("Research")
            llm = self._get_llm()
            agent = create_react_agent(
                llm, 
                READ_ONLY_META_TOOLS, 
                prompt=(
                    "Liste campanhas Meta ativas usando a ferramenta. Responda curto: id, nome, status, gasto, cliques, conversões, CPA. "
                    "ATENÇÃO: VOCÊ DEVE USAR APENAS OS IDS NUMÉRICOS REAIS (EX: 123456789) RECEBIDOS PELA FERRAMENTA. "
                    "NUNCA USE PLACEHOLDERS COMO 'ID da campanha X' OU NOMES DAS CAMPANHAS NO LUGAR DO ID."
                )
            )
            
            logger.info("Invocando Agent Research para buscar campanhas...")
            try:
                result = await agent.ainvoke(self._compact_state(state), config)
                logger.info("Agent Research concluiu a pesquisa.")
                return {"messages": [result["messages"][-1]], "executed_agents": ["research"]}
            except Exception as e:
                logger.error(f"ERRO no Research Agent: {str(e)}")
                raise

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception(should_retry_agent_error),
            reraise=True
        )
        async def analyzer_node(state: AgentState, config: RunnableConfig):
            global_logs.set_active_agent("Analyzer")
            llm = self._get_llm(os.getenv("GROQ_ANALYZER_MODEL", ANALYZER_GROQ_MODEL))
            agent = create_react_agent(
                llm, 
                READ_ONLY_META_TOOLS, 
                prompt=(
                    "Analise KPIs Meta. Use dados da ferramenta. Responda em bullets curtos: problema, evidência, ação. "
                    "ATENÇÃO: VOCÊ DEVE USAR APENAS OS IDS NUMÉRICOS REAIS (EX: 123456789) RECEBIDOS PELA FERRAMENTA. "
                    "NUNCA USE PLACEHOLDERS COMO 'ID da campanha X' OU NOMES DAS CAMPANHAS NO LUGAR DO ID."
                )
            )
            
            logger.info("Invocando Agent Analyzer para processar métricas...")
            try:
                result = await agent.ainvoke(self._compact_state(state), config)
                logger.info("Agent Analyzer finalizou a análise de performance.")
                return {"messages": [result["messages"][-1]], "executed_agents": ["analyzer"]}
            except Exception as e:
                logger.error(f"ERRO no Analyzer Agent: {str(e)}")
                raise

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception(should_retry_agent_error),
            reraise=True
        )
        async def operator_node(state: AgentState, config: RunnableConfig):
            global_logs.set_active_agent("Operator")
            llm = self._get_llm()
            agent = create_react_agent(
                llm,
                OPERATOR_TOOLS,
                prompt=(
                    "Execute ações Meta somente quando pedidas. "
                    "No fluxo autônomo, aja APENAS com ferramentas de mutação: "
                    "tool_pause_campaign ou tool_increase_budget. "
                    "As ferramentas de leitura existem só para validação de contexto quando necessário. "
                    "Confirme ID e resultado. "
                    "ATENÇÃO: VOCÊ DEVE USAR APENAS OS IDS NUMÉRICOS REAIS (EX: 123456789) RECEBIDOS PELA FERRAMENTA. "
                    "NUNCA USE PLACEHOLDERS COMO 'ID da campanha X' OU NOMES DAS CAMPANHAS NO LUGAR DO ID."
                )
            )
            
            logger.info("Invocando Agent Operator para executar ação...")
            try:
                result = await agent.ainvoke(self._compact_state(state), config)
                logger.info("Agent Operator concluiu a execução da tarefa.")
                return {"messages": [result["messages"][-1]], "executed_agents": ["operator"]}
            except Exception as e:
                logger.error(f"ERRO no Operator Agent: {str(e)}")
                raise

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception(should_retry_agent_error),
            reraise=True
        )
        async def memory_node(state: AgentState, config: RunnableConfig):
            global_logs.set_active_agent("Memory")
            llm = self._get_llm()
            agent = create_react_agent(
                llm, 
                [tool_save_memory, tool_search_memory], 
                prompt=(
                    "Use memória só quando pedido: salvar insight ou buscar contexto. Responda curto. "
                    "ATENÇÃO: VOCÊ DEVE USAR APENAS OS IDS NUMÉRICOS REAIS (EX: 123456789) RECEBIDOS PELA FERRAMENTA. "
                    "NUNCA USE PLACEHOLDERS COMO 'ID da campanha X' OU NOMES DAS CAMPANHAS NO LUGAR DO ID."
                )
            )
            
            logger.info("Invocando Agent Memory Keeper para acessar ChromaDB...")
            try:
                result = await agent.ainvoke(self._compact_state(state), config)
                logger.info("Agent Memory Keeper atualizou a memória vetorial.")
                return {"messages": [result["messages"][-1]], "executed_agents": ["memory_keeper"]}
            except Exception as e:
                logger.error(f"ERRO no Memory Keeper Agent: {str(e)}")
                raise

        builder.add_node("research", research_node)
        builder.add_node("analyzer", analyzer_node)
        builder.add_node("operator", operator_node)
        builder.add_node("memory_keeper", memory_node)
        
        # --- LÓGICA DE ROTEAMENTO ---
        
        def is_autonomous_flow(state: AgentState) -> bool:
            user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
            if not user_messages:
                return False

            first_message = user_messages[0].content.lower()
            return any(marker in first_message for marker in (
                "inspeção autônoma",
                "inspecao autonoma",
                "rotina autônoma",
                "rotina autonoma",
                "agent research",
            ))

        def router_logic(state: AgentState):
            if is_autonomous_flow(state):
                return "research"

            user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
            if not user_messages:
                return "research"
                
            last_message = user_messages[-1].content.lower()
            
            operator_keywords = ["pausar", "parar", "cancelar", "budget", "orçamento", "orcamento", "aumentar", "diminuir", "alterar", "mudar", "atualizar"]
            if any(k in last_message for k in operator_keywords) and not any(k in last_message for k in ["métrica", "metrica", "performance"]):
                 return "operator"

            memory_keywords = ["salvar", "guardar", "memória", "memoria", "histórico", "historico", "aprendizado", "esquecer", "recordar"]
            if any(k in last_message for k in memory_keywords):
                return "memory_keeper"
            
            analyzer_keywords = ["métrica", "metrica", "performance", "roas", "analisar", "resultado", "cpc", "ctr", "investimento", "gasto", "clique"]
            if any(k in last_message for k in analyzer_keywords):
                return "analyzer"
                
            return "research"

        builder.add_conditional_edges(START, router_logic, {
            "research": "research",
            "analyzer": "analyzer",
            "operator": "operator",
            "memory_keeper": "memory_keeper"
        })
        
        def route_after_research(state: AgentState):
            if is_autonomous_flow(state) and "analyzer" not in state.get("executed_agents", []):
                return "analyzer"
            return END

        def route_after_analyzer(state: AgentState):
            if not is_autonomous_flow(state) or "operator" in state.get("executed_agents", []):
                return END

            last_message = state["messages"][-1].content.lower() if state.get("messages") else ""
            if any(marker in last_message for marker in ("pausar", "pause", "pausa", "roas menor", "roas <")):
                return "operator"
            return END

        builder.add_conditional_edges("research", route_after_research, {
            "analyzer": "analyzer",
            END: END
        })
        builder.add_conditional_edges("analyzer", route_after_analyzer, {
            "operator": "operator",
            END: END
        })
        builder.add_edge("operator", END)
        builder.add_edge("memory_keeper", END)
        
        return builder.compile(checkpointer=MemorySaver())

    async def run(self, message: str) -> str:
        logger.info(f"Iniciando orquestração para: {message}")
        config = {"configurable": {"thread_id": "session_1"}}
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "executed_agents": [],
            "next_agents": [],
            "intermediate_data": {}
        }
        
        final_content = "Não foi possível processar sua solicitação."
        try:
            async for event in self.graph.astream(initial_state, config, stream_mode="values"):
                if event and "messages" in event:
                    final_content = event["messages"][-1].content
            
            global_logs.set_active_agent("Router")
            return final_content
        except Exception as e:
            global_logs.set_active_agent("Router")
            if is_tool_validation_bad_request(e):
                logger.warning(f"Erro de validação de tool no provedor: {e}")
                return TOOL_VALIDATION_ERROR_MESSAGE

            logger.exception(f"Erro crítico na orquestração: {e}")
            return f"Ocorreu um erro crítico no motor de agentes: {str(e)}"
