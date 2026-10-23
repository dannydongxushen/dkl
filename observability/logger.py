import os
import sys
import json
from datetime import datetime, timezone
from langfuse import Langfuse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from config import config

OBS_CONFIG = config.get("observability", {})
LOG_FILE = OBS_CONFIG.get("log_file")

class ObservabilityLogger:
    def __init__(self):
        self.log_file = LOG_FILE
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        self.langfuse = None
        if OBS_CONFIG.get("enabled", False):
            try:
                self.langfuse = Langfuse(
                    public_key=OBS_CONFIG.get("public_key", "pk-lf-local"),
                    secret_key=OBS_CONFIG.get("secret_key", "sk-lf-local"),
                    host=OBS_CONFIG.get("base_url", "http://localhost:23100")
                )
                print("Litefuse observability initialized.")
            except Exception as e:
                print(f"Failed to initialize Litefuse: {e}")

    def log_call(self, model_name: str, prompt_tokens: int, completion_tokens: int, latency_ms: float, input_messages: list, output_text: str):
        record = {
            "type": "llm_call",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "latency_ms": round(latency_ms, 2),
            "input_preview": str(input_messages)[:200],
            "output_preview": str(output_text)[:200]
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"Failed to write local log: {e}")

        if self.langfuse:
            try:
                generation = self.langfuse.start_observation(
                    name="llm_completion",
                    as_type="generation",
                    model=model_name,
                    input=input_messages,
                    output=output_text,
                    usage_details={
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens
                    }
                )
                generation.end()
            except Exception as e:
                print(f"Failed to send trace to Litefuse: {e}")

    def log_retrieval(self, component: str, query: str, latency_ms: float, result_count: int):
        record = {
            "type": "retrieval",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": component,
            "latency_ms": round(latency_ms, 2),
            "result_count": result_count,
            "query": query
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"Failed to write local log: {e}")

        if self.langfuse:
            try:
                span = self.langfuse.start_observation(
                    name=component,
                    as_type="span",
                    input=query,
                    metadata={"latency_ms": latency_ms, "result_count": result_count}
                )
                span.end()
            except Exception as e:
                print(f"Failed to send trace to Litefuse: {e}")

obs_logger = ObservabilityLogger()