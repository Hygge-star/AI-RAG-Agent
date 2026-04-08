from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import chat, health

app = FastAPI(
    title="RAG + LangGraph Agent API",
    description="基于 RAG 的智能问答系统",
    version="1.0.0"
)

# 允许跨域（生产环境请限制来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])

@app.get("/")
async def root():
    return {"message": "RAG Agent API is running. Visit /docs for Swagger documentation."}