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

from domain.models import ChatMessage, AgentResponse

# Import das Ferramentas Reais
from application.use_cases.tools.meta_tools import tool_get_active_campaigns, tool_get_campaign_metrics
from application.use_cases.tools.memory_tools import tool_save_memory, tool_search_memory

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
            state_modifier="Você é o Especialista em Pesquisa do Meta Ads. Sua missão é buscar e listar campanhas ativas para dar visibilidade ao usuário."
        )
        
        # 2. Agent Analyzer: Analisa performance e métricas
        self.analyzer_agent = create_react_agent(
            self.llm, 
            [tool_get_campaign_metrics], 
            state_modifier="Você é o Analista de Performance. Sua missão é mergulhar nos dados de ROAS, CPC e conversões para fornecer insights de otimização."
        )
        
        # 3. Agent Memory Keeper: Gerencia o conhecimento no ChromaDB
        self.memory_keeper_agent = create_react_agent(
            self.llm, 
            [tool_save_memory, tool_search_memory], 
            state_modifier="Você é o Guardião da Memória. Sua missão é salvar insights importantes e recuperar contextos históricos no ChromaDB."
        )
        
        builder = StateGraph(AgentState)
        
        # --- DEFINIÇÃO DOS NODES ---
        
        async def research_node(state: AgentState, config: RunnableConfig):
            print(f"\n[ORCHESTRATOR] Invocando Agent Research...")
            try:
                result = await self.research_agent.ainvoke(state, config)
                return {"messages": [result["messages"][-1]], "executed_agents": ["research"]}
            except Exception as e:
                print(f"[ERROR] Falha no Research Agent: {e}")
                return {"messages": [AIMessage(content=f"Erro ao pesquisar campanhas: {str(e)}")]}

        async def analyzer_node(state: AgentState, config: RunnableConfig):
            print(f"\n[ORCHESTRATOR] Invocando Agent Analyzer...")
            try:
                result = await self.analyzer_agent.ainvoke(state, config)
                return {"messages": [result["messages"][-1]], "executed_agents": ["analyzer"]}
            except Exception as e:
                print(f"[ERROR] Falha no Analyzer Agent: {e}")
                return {"messages": [AIMessage(content=f"Erro ao analisar métricas: {str(e)}")]}

        async def memory_node(state: AgentState, config: RunnableConfig):
            print(f"\n[ORCHESTRATOR] Invocando Agent Memory Keeper...")
            try:
                result = await self.memory_keeper_agent.ainvoke(state, config)
                return {"messages": [result["messages"][-1]], "executed_agents": ["memory_keeper"]}
            except Exception as e:
                print(f"[ERROR] Falha no Memory Keeper Agent: {e}")
                return {"messages": [AIMessage(content=f"Erro ao acessar memória: {str(e)}")]}

        builder.add_node("research", research_node)
        builder.add_node("analyzer", analyzer_node)
        builder.add_node("memory_keeper", memory_node)
        
        # --- LÓGICA DE ROTEAMENTO ---
        
        def router_logic(state: AgentState):
            # Lógica simples de roteamento baseada na última mensagem
            last_message = state["messages"][-1].content.lower()
            
            if any(k in last_message for k in ["métrica", "performance", "roas", "analisar", "id"]):
                return "analyzer"
            if any(k in last_message for k in ["memória", "histórico", "salvar", "contexto", "guardar"]):
                return "memory_keeper"
            return "research"

        builder.add_conditional_edges(START, router_logic, {
            "research": "research",
            "analyzer": "analyzer",
            "memory_keeper": "memory_keeper"
        })
        
        builder.add_edge("research", END)
        builder.add_edge("analyzer", END)
        builder.add_edge("memory_keeper", END)
        
        self.memory = MemorySaver()
        self.graph = builder.compile(checkpointer=self.memory)

    async def run(self, message: str) -> str:
        print(f"\n[SYSTEM] Iniciando processamento: {message}")
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
            return final_content
        except Exception as e:
            print(f"[FATAL ERROR] Erro na orquestração: {e}")
            return f"Ocorreu um erro crítico no motor de agentes: {str(e)}"
