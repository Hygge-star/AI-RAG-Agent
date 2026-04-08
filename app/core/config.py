import yaml
from pathlib import Path
from pydantic import BaseModel
from functools import lru_cache
from typing import Any, Dict

# 项目根目录（假设本文件位于 app/core/config.py，向上三级到项目根）
ROOT_DIR = Path(__file__).parent.parent.parent


# ========== 定义各个配置的模型（请根据你的 YAML 实际字段调整）==========
class AgentConfig(BaseModel):
    external_data_path: str="data/external/records.csv"

class ChromaConfig(BaseModel):
    collection_name: str="agent"
    persist_directory: str="chroma_db"
    k:int=3
    data_path:str="data"
    md5_hex_store: str="md5.text"
    allow_knowledge_file_type: list=["txt", "pdf"]

    chunk_size: int=200
    chunk_overlap: int=20
    separators: list=["\n\n", "\n", ",", ".", "?", "。", "，", "！", "？", " ", ""]


class PromptsConfig(BaseModel):
    main_prompt_path: str="prompts / main_prompt.txt"
    rag_summarize_prompt_path: str="prompts / rag_summarize.txt"
    report_prompt_path: str="prompts / report_prompt.txt"

class RagConfig(BaseModel):
    chat_model_name: str="qwen3 - max"
    embedding_model_name: str="text - embedding - v4"

class AppConfig(BaseModel):
    agent: AgentConfig
    chroma: ChromaConfig
    prompts: PromptsConfig
    rag: RagConfig


# ============================================================

def _load_yaml(file_name: str) -> Dict[str, Any]:
    yaml_path = ROOT_DIR / "config" / file_name
    if not yaml_path.exists():
        return {}  # 文件不存在则返回空，使用默认值
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data if data else {}


@lru_cache()
def get_config() -> AppConfig:
    agent_data = _load_yaml("agent.yml")
    chroma_data = _load_yaml("chroma.yml")
    prompts_data = _load_yaml("prompts.yml")
    rag_data = _load_yaml("rag.yml")

    return AppConfig(
        agent=AgentConfig(**agent_data),
        chroma=ChromaConfig(**chroma_data),
        prompts=PromptsConfig(**prompts_data),
        rag=RagConfig(**rag_data)
    )


# 全局配置实例
config = get_config()