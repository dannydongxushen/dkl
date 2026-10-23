# ai-service/rag_engine.py
import os
import sys
import time
import torch
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from reranking import reranker_instance
from observability.logger import obs_logger

CHROMA_DIR = config["paths"]["chroma_dir"]
COLLECTION_NAME = config["rag"]["collection_name"]
EMBEDDING_MODEL = config["rag"]["embedding_model"]

class QwenEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(
            model_name, 
            model_kwargs={"torch_dtype": torch.float32}
        )

    def __call__(self, input: Documents) -> Embeddings:
        return self.model.encode(input, normalize_embeddings=True).tolist()

class RAGEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.embedding_fn = QwenEmbeddingFunction(EMBEDDING_MODEL)
        self.collection = self.client.get_collection(
            name=COLLECTION_NAME, 
            embedding_function=self.embedding_fn
        )

    def search(self, query: str, initial_top_k: int = 5) -> list:
        start_time = time.time()
        results = self.collection.query(
            query_texts=[query],
            n_results=initial_top_k
        )
        latency_ms = (time.time() - start_time) * 1000
        
        if not results["documents"] or not results["documents"][0]:
            obs_logger.log_retrieval(component="ChromaDB", query=query, latency_ms=latency_ms, result_count=0)
            return []
            
        retrieved_docs = []
        for i in range(len(results["documents"][0])):
            retrieved_docs.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "id": results["ids"][0][i]
            })
            
        obs_logger.log_retrieval(component="ChromaDB", query=query, latency_ms=latency_ms, result_count=len(retrieved_docs))
            
        reranked_docs = reranker_instance.rerank(query, retrieved_docs)
        return reranked_docs

rag_engine_instance = RAGEngine()