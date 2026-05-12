import json
from langchain_core.tools import tool
from infrastructure.vector_store import VectorStore

vector_store = VectorStore()

@tool
def tool_save_memory(insight: str, context: str = "{}") -> str:
    """Salva um insight, aprendizado ou análise importante na memória de longo prazo (ChromaDB).
    Use esta ferramenta sempre que descobrir algo relevante sobre a performance das campanhas ou 
    tomar uma decisão que deva ser lembrada no futuro. 
    O 'context' deve ser um JSON string com metadados adicionais se necessário."""
    try:
        context_dict = json.loads(context)
    except:
        context_dict = {"raw_context": context}
        
    vector_store.save_insight(insight, context_dict)
    return "Insight salvo com sucesso na memória de longo prazo."

@tool
def tool_search_memory(query: str, k: int = 3) -> str:
    """Busca na memória de longo prazo (ChromaDB) por contextos históricos, análises passadas e aprendizados.
    Use esta ferramenta para verificar se já houve análises similares ou se existem diretrizes 
    salvas anteriormente que possam ajudar na tarefa atual."""
    results = vector_store.search_history(query, k=k)
    if not results["results"]:
        return "Nenhum histórico relevante encontrado na memória."
    
    return json.dumps(results, indent=2, ensure_ascii=False)
