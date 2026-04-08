import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径，以便导入原有模块
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from rag.rag_service import RagSummarizeService

_rag_service_instance = None

def get_rag_service() -> RagSummarizeService:
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RagSummarizeService()
    return _rag_service_instance