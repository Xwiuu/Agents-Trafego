from typing import Dict, List
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
    
    def add_insight(self, insight: str, context: str = "{}"):
        """Salva aprendizados críticos no ChromaDB."""
        from datetime import datetime
        self.collection.add(
            ids=[f"insight_{datetime.now().timestamp()}"],
            documents=[insight],
            metadatas=[{"timestamp": str(datetime.now()), "context": context}]
        )
    
    def search_context(self, query: str, n_results: int = 3):
        """Busca no ChromaDB por análises anteriores e contextos históricos."""
        results = self.collection.query(query_texts=[query], n_results=n_results)
        return {"source": "ChromaDB", "status": "success", "results": results.get('documents', [])}