import json
from datetime import datetime
from typing import Dict, List, Any
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings

class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.chroma_client.get_or_create_collection(
            name="meta_ads_intelligence_v5",
            embedding_function=self._get_embedding_function()
        )
    
    def _get_embedding_function(self):
        """Wrapper para integrar Embeddings do LangChain com o ChromaDB."""
        from chromadb.api.types import EmbeddingFunction
        class LangChainEmbeddingFunction(EmbeddingFunction):
            def __init__(self, langchain_embeddings):
                self.langchain_embeddings = langchain_embeddings

            def __call__(self, input):
                return self.langchain_embeddings.embed_documents(input)

            def embed_documents(self, input):
                return self.langchain_embeddings.embed_documents(input)

            def embed_query(self, query: str) -> List[float]:
                return self.langchain_embeddings.embed_query(query)
        
        return LangChainEmbeddingFunction(self.embeddings_model)
    
    def save_insight(self, insight: str, context: dict = {}):
        """Salva aprendizados críticos e insights de performance no ChromaDB para uso futuro."""
        self.collection.add(
            ids=[f"insight_{datetime.now().timestamp()}"],
            documents=[insight],
            metadatas=[{"timestamp": str(datetime.now()), "context": json.dumps(context)}]
        )
    
    def search_history(self, query: str, k: int = 3):
        """Busca no ChromaDB por análises anteriores, decisões passadas e contextos históricos."""
        results = self.collection.query(query_texts=[query], n_results=k)
        return {
            "source": "ChromaDB",
            "status": "success",
            "results": results.get('documents', [[]])[0] if results.get('documents') else []
        }
