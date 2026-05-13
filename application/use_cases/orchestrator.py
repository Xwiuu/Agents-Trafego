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
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from domain.models import ChatMessage, AgentResponse

# Import das Ferramentas Reais
from application.use_cases.tools.meta_tools import tool_get_active_campaigns, tool_get_campaign_metrics
from application.use_cases.tools.memory_tools import tool_save_memory, tool_search_memory
from application.use_cases.tools.operator_tools import tool_pause_campaign, tool_increase_budget
from infrastructure.logger import global_logs, logger

# --- ESTADO DO AGENTE ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_agents: List[str]
    executed_agents: Annotated[List[str], operator.add]
    intermediate_data: Dict[str, Any]

def trim_messages(messages: List[BaseMessage], max_messages: int = 10) -> List[BaseMessage]:
    if not messages:
        return []
    if len(messages) <= max_messages:
        return messages
    return [messages[0]] + list(messages[-(max_messages-1):])

# --- ORQUESTRADOR ---
class RouterSystem:
    def __init__(self, api_key: str):
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.1-8b-instant",
            temperature=0.1
        )
        
        # 1. Agent Research: Busca dados e campanhas ativas
        self.research_agent = create_react_agent(
            self.llm, 
            [tool_get_active_campaigns], 
            prompt="Você é o Especialista em Pesquisa do Meta Ads. Sua missão é buscar e listar campanhas ativas para dar visibilidade ao usuário."
        )
        
        # 2. Agent Analyzer: Analisa performance e métricas
        self.analyzer_agent = create_react_agent(
            self.llm, 
            [tool_get_campaign_metrics], 
            prompt="Você é o Analista de Performance. Sua missão é mergulhar nos dados de ROAS, CPC e conversões para fornecer insights de otimização."
        )

        # 3. Agent Operator: Executa ações de mutação (Pause, Budget Update)
        self.operator_agent = create_react_agent(
            self.llm,
            [tool_pause_campaign, tool_increase_budget],
            prompt="""Você é o Agente Operador (Executor). Sua missão é executar alterações reais nas campanhas do Meta Ads.
            - Se o usuário pedir para PAUSAR, use 'tool_pause_campaign'.
            - Se o usuário pedir para ALTERAR/AUMENTAR/DIMINUIR orçamento, use 'tool_increase_budget'.
            Sempre confirme o ID da campanha antes de agir. Após a execução bem sucedida ou falha, reporte o status claramente para o usuário."""
        )
        
        # 4. Agent Memory Keeper: Gerencia o conhecimento no ChromaDB
        self.memory_keeper_agent = create_react_agent(
            self.llm, 
            [tool_save_memory, tool_search_memory], 
            prompt="Você é o Guardião da Memória. Sua missão é salvar insights importantes e recuperar contextos históricos no ChromaDB."
        )
        
        builder = StateGraph(AgentState)
        
        # --- DEFINIÇÃO DOS NODES COM RETRIES ---
        
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type(Exception),
            reraise=True
        )
        async def research_node(state: AgentState, config: RunnableConfig):
            global_logs.set_active_agent("Research")
            logger.info("Invocando Agent Research para buscar campanhas...")
            try:
                result = await self.research_agent.ainvoke(state, config)
                logger.info("Agent Research concluiu a pesquisa.")
                return {"messages": [result["messages"][-1]], "executed_agents": ["research"]}
            except Exception as e:
                logger.error(f"ERRO no Research Agent: {str(e)}")
                raise

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type(Exception),
            reraise=True
        )
        async def analyzer_node(state: AgentState, config: RunnableConfig):
            global_logs.set_active_agent("Analyzer")
            logger.info("Invocando Agent Analyzer para processar métricas...")
            try:
                result = await self.analyzer_agent.ainvoke(state, config)
                logger.info("Agent Analyzer finalizou a análise de performance.")
                return {"messages": [result["messages"][-1]], "executed_agents": ["analyzer"]}
            except Exception as e:
                logger.error(f"ERRO no Analyzer Agent: {str(e)}")
                raise

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type(Exception),
            reraise=True
        )
        async def operator_node(state: AgentState, config: RunnableConfig):
            global_logs.set_active_agent("Operator")
            logger.info("Invocando Agent Operator para executar ação...")
            try:
                result = await self.operator_agent.ainvoke(state, config)
                logger.info("Agent Operator concluiu a execução da tarefa.")
                return {"messages": [result["messages"][-1]], "executed_agents": ["operator"]}
            except Exception as e:
                logger.error(f"ERRO no Operator Agent: {str(e)}")
                raise

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type(Exception),
            reraise=True
        )
        async def memory_node(state: AgentState, config: RunnableConfig):
            global_logs.set_active_agent("Memory")
            logger.info("Invocando Agent Memory Keeper para acessar ChromaDB...")
            try:
                result = await self.memory_keeper_agent.ainvoke(state, config)
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
        
        def router_logic(state: AgentState):
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
        
        builder.add_edge("research", END)
        builder.add_edge("analyzer", END)
        builder.add_edge("operator", END)
        builder.add_edge("memory_keeper", END)
        
        self.memory = MemorySaver()
        self.graph = builder.compile(checkpointer=self.memory)

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
            logger.exception(f"Erro crítico na orquestração: {e}")
            return f"Ocorreu um erro crítico no motor de agentes: {str(e)}"
