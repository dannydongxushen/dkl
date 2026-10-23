# ai-service/reranking.py
import os
import sys
import time
import torch
from sentence_transformers import CrossEncoder

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from config import config
from observability.logger import obs_logger

RERANKER_MODEL = config["rag"]["reranker_model"]
RERANK_TOP_K = config["rag"]["rerank_top_k"]

class Reranker:
    def __init__(self):
        self.model = CrossEncoder(
            RERANKER_MODEL,
            model_kwargs={"torch_dtype": torch.float32}
        )
        self.top_k = RERANK_TOP_K

    def rerank(self, query: str, documents: list) -> list:
        if not documents:
            return []
        
        start_time = time.time()
        
        pairs = [[query, doc["text"]] for doc in documents]
        scores = self.model.predict(pairs)
        
        latency_ms = (time.time() - start_time) * 1000
        
        for idx, score in enumerate(scores):
            documents[idx]["rerank_score"] = float(score)
            
        sorted_docs = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
        top_docs = sorted_docs[:self.top_k]
        
        obs_logger.log_retrieval(
            component="Reranker", 
            query=query, 
            latency_ms=latency_ms, 
            result_count=len(top_docs)
        )
        
        return top_docs

reranker_instance = Reranker()