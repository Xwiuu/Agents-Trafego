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

# --- FERRAMENTAS ---
@tool
def fetch_meta_api_data(query: str) -> str:
    """Busca dados de campanhas, insights e performance na Meta Ads API."""
    return json.dumps({"source": "Meta API", "status": "simulated", "message": "Conectando ao Meta Ads..."}, indent=2)

@tool
def search_memory_for_context(query: str) -> str:
    """Busca no ChromaDB por análises anteriores."""
    return json.dumps({"source": "ChromaDB", "status": "success", "results": []}, indent=2)

# --- ORQUESTRADOR ---
class RouterSystem:
    def __init__(self, api_key: str):
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.1-8b-instant",
            temperature=0.1
        )
        
        # Agentes
        self.research_agent = create_react_agent(self.llm, [fetch_meta_api_data, search_memory_for_context], prompt="Você é um pesquisador de tráfego.")
        
        builder = StateGraph(AgentState)
        
        async def research_node(state: AgentState, config: RunnableConfig):
            result = await self.research_agent.ainvoke(state, config)
            return {"messages": [result["messages"][-1]], "executed_agents": ["research"]}

        builder.add_node("research", research_node)
        builder.add_edge(START, "research")
        builder.add_edge("research", END)
        
        self.memory = MemorySaver()
        self.graph = builder.compile(checkpointer=self.memory)

    async def run(self, message: str) -> str:
        config = {"configurable": {"thread_id": "default"}}
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "executed_agents": [],
            "next_agents": [],
            "intermediate_data": {}
        }
        
        final_content = ""
        async for event in self.graph.astream(initial_state, config, stream_mode="values"):
            if event and "messages" in event:
                final_content = event["messages"][-1].content
        
        return final_content
