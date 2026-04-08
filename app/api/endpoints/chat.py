from fastapi import APIRouter, Depends, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.rag_wrapper import get_rag_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, rag_service=Depends(get_rag_service)):
    try:
        print(f"收到消息: {request.message}")
        docs = rag_service.retriever_docs(request.message)
        print(f"检索到 {len(docs)} 个文档")
        if not docs:
            print("警告：未检索到任何文档，请检查 chroma_db 目录")
        reply = rag_service.rag_summarize(request.message)
        print(f"回复: {reply}")
        return ChatResponse(reply=reply, session_id=request.session_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))