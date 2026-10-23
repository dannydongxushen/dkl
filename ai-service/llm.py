import os
import sys
import time
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from config import config
from observability.logger import obs_logger

LLM_CONFIG = config["llm"]
BASE_URL = LLM_CONFIG["base_url"]
MODEL_NAME = LLM_CONFIG["model_name"]
API_KEY = LLM_CONFIG.get("api_key")

if not API_KEY:
    active_provider = config["llm"].get("active_provider", "unknown")
    raise ValueError(
        f"API Key is missing for provider '{active_provider}'. "
        f"Please set the required environment variable before starting the application."
    )

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

class LLMService:
    def __init__(self):
        self.client = client
        self.model = MODEL_NAME

    def chat(self, messages: list, tools: list | None = None):
        start_time = time.time()
        
        kwargs = {
            "model": self.model,
            "messages": messages
        }
        if tools:
            kwargs["tools"] = tools
            
        response = self.client.chat.completions.create(**kwargs)
        
        latency_ms = (time.time() - start_time) * 1000
        
        if response.usage:
            obs_logger.log_call(
                model_name=self.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                latency_ms=latency_ms,
                input_messages=messages,
                output_text=response.choices[0].message.content or ""
            )
            
        return response

llm_instance = LLMService()