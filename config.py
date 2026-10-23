# config.py
import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

config["paths"]["data_dir"] = os.path.join(BASE_DIR, config["paths"]["data_dir"])
config["paths"]["sqlite_db"] = os.path.join(BASE_DIR, config["paths"]["sqlite_db"])
config["paths"]["chroma_dir"] = os.path.join(BASE_DIR, config["paths"]["chroma_dir"])

obs_log_file = config.get("observability", {}).get("log_file", "observability/logs/llm_calls.jsonl")
if "observability" not in config:
    config["observability"] = {}
config["observability"]["log_file"] = os.path.join(BASE_DIR, obs_log_file)

api_key_env = config["llm"]["api_key_env"]
config["llm"]["api_key"] = os.environ.get(api_key_env)