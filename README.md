# RAG Agent 智能知识库助手

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0-blue?logo=langchain)](https://langchain-ai.github.io/langgraph/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个从原型验证到工程化封装的 RAG 智能问答系统。项目最初使用 Streamlit 快速搭建知识库对话界面，随后引入 LangGraph 重构对话流程控制，最终采用 FastAPI 提供标准 RESTful API，完成从脚本到服务的演进。

## 项目演进

| 阶段 | 技术实现 | 核心产出 |
|------|----------|----------|
| 原型验证 | Streamlit + LangChain + ChromaDB | 快速搭建可交互的知识库问答界面，验证 RAG 可行性 |
| 流程升级 | LangGraph 替换 LangChain 链式调用 | 实现状态图驱动的 Agent，支持条件分支与工具调用 |
| 服务化封装 | FastAPI + Pydantic | 提供标准 RESTful API 与 Swagger 交互文档，支持部署 |

## 核心特性

- 多模型支持：同时接入阿里云通义千问 API 与本地 Ollama 模型，可配置切换
- RAG 检索增强：基于 ChromaDB 向量存储，实现文档切片、向量召回与上下文注入
- 对话流程编排：使用 LangGraph 构建状态图，替代传统 Chain，支持复杂对话逻辑
- 会话记忆管理：通过 session_id 维护对话历史，实现多轮上下文连续对话
- 标准化 API：FastAPI 提供 RESTful 接口，自动生成 Swagger UI 交互文档
- 工程化结构：分层架构设计（API 层、服务层、核心引擎层），便于维护与扩展

## 技术栈

| 类别 | 技术选型 |
|------|----------|
| Web 框架 | FastAPI, Uvicorn (API 服务) / Streamlit (原型界面) |
| AI 编排 | LangGraph (状态图), LangChain (基础组件) |
| 向量检索 | ChromaDB, OpenAI Embeddings / 本地 Embedding |
| 大语言模型 | 阿里云通义千问 API / Ollama 本地模型 (可配置切换) |
| 数据校验 | Pydantic v2 |
| 部署 | Docker, Uvicorn |

### Swagger UI 交互文档
访问 `/docs` 即可在线调试所有接口。

### 对话示例
```json
POST /api/v1/chat
{
  "message": "扫地机器人如何保养？",
  "session_id": "user_001",
  "stream": false
}

Response 200:
{
  "reply": "建议每周清理滚刷缠绕物，每月清洗滤网，避免在潮湿环境使用...",
  "session_id": "user_001"
}
```

## 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/你的用户名/rag-agent-fastapi.git
cd rag-agent-fastapi
```

### 2. 安装依赖
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置环境变量
创建 `.env` 文件，根据使用的模型选择配置：
```env
# 阿里云通义千问
DASHSCOPE_API_KEY=sk-xxxx

# 或 OpenAI 兼容 API
OPENAI_API_KEY=sk-xxxx
OPENAI_BASE_URL=https://api.openai.com/v1

# 本地 Ollama 无需密钥，在配置文件中指定模型名即可
```

### 4. 准备知识库
将文档放入 `data/` 目录，执行向量化导入：
```bash
python -c "from rag.vector_store import VectorStoreService; VectorStoreService().load_document()"
```

### 5. 启动服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：
- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/v1/health

### 6. 可选：运行 Streamlit 原型界面
```bash
streamlit run streamlit_app.py
```

## 项目结构

```
rag-agent-fastapi/
├── app/                         # FastAPI 应用主目录
│   ├── main.py                  # 应用入口，路由注册
│   ├── api/                     # 接口路由层
│   │   └── endpoints/
│   │       ├── chat.py          # 对话接口 POST /api/v1/chat
│   │       └── health.py        # 健康检查 GET /api/v1/health
│   ├── models/                  # Pydantic 请求/响应模型
│   │   └── chat.py
│   └── services/                # 业务逻辑适配层
│       └── rag_wrapper.py       # 调用原有 RAG 服务的单例包装
├── rag/                         # 原有 RAG 核心代码
│   ├── rag_service.py           # 检索增强生成服务 (RagSummarizeService)
│   └── vector_store.py          # ChromaDB 向量存储操作
├── agent/                       # LangGraph Agent 定义（可选）
├── chroma_db/                   # 向量数据库持久化目录
├── config/                      # YAML 配置文件（chroma.yml, prompts.yml 等）
├── data/                        # 原始知识库文件（PDF/TXT）
├── model/                       # LLM 与 embedding 模型工厂
├── prompts/                     # Prompt 模板
├── utils/                       # 工具函数（日志、文件处理、路径辅助）
├── tests/                       # 单元测试
├── .env                         # 环境变量（API Keys）
├── Dockerfile                   # Docker 镜像构建文件
├── requirements.txt
└── README.md
```

## API 接口

| Method | Endpoint | 描述 |
|--------|----------|------|
| POST | `/api/v1/chat` | 发送对话消息 |
| GET | `/api/v1/health` | 服务健康检查 |

详细参数请访问 `/docs` 查看 Swagger 文档。

## Docker 部署

```bash
docker build -t rag-agent-api .
docker run -d -p 8000:8000 --env-file .env rag-agent-api
```

## 后续规划

- 支持流式输出 (Server-Sent Events)
- 增加用户认证与速率限制
- 前端对话界面重构为 React/Vue

## 接入FastAPI的好处

### 1. 从「本地工具」升级为「可远程调用的服务」
- **之前**：可能是 Streamlit 本地界面，或只能在 Python 脚本里直接调用 Agent。
- **之后**：任何语言（Java、Go、JavaScript）或任何设备（Web、移动端、微服务）都能通过 HTTP 请求调用你的智能体，例如：
  ```bash
  curl -X POST http://localhost:8000/api/v1/chat -H "Content-Type: application/json" -d '{"message":"你好"}'
  ```

### 2. 自动生成交互式 API 文档
- FastAPI 自动提供 Swagger UI (`/docs`) 和 ReDoc (`/redoc`)，团队成员可以直接在浏览器里测试聊天接口、查看请求/响应模型，无需编写额外文档。

### 3. 支持异步并发与高性能
- FastAPI 基于 Starlette（异步 ASGI 框架），性能远高于 Flask。如果你的 LangGraph 或 RAG 中有异步 IO 操作（如异步向量库、HTTP 请求），可以轻松集成 `async/await`，显著提升吞吐量。

### 4. 标准化依赖注入与中间件
- 你可以在 `dependencies.py` 中管理 Agent 单例、数据库连接池、API Key 校验等。
- 轻松添加 CORS 中间件（用于前端跨域）、日志中间件、限流中间件等。

### 5. 便于容器化部署与弹性伸缩
- 有了 `main.py` 和 Dockerfile，可以快速打包成镜像，部署到 Kubernetes、云服务器或 Serverless 平台。
- 结合负载均衡（如 Nginx），可以水平扩展多个 FastAPI 副本，每个副本独立运行 Agent。

### 6. 前后端彻底分离
- 原来的 Streamlit 前端（如果有）可以保留，但改为通过 `requests` 调用 FastAPI 后端。
- 未来可以用 React/Vue 构建专业前端，或直接接入钉钉/企业微信机器人、Slack Bot、Telegram Bot 等。

### 7. 更完善的项目结构与可维护性
- 按照 `app/`、`api/`、`core/`、`models/`、`services/` 分层后，业务逻辑（`agent/`、`rag/`）与 HTTP 层解耦。
- 单元测试更容易编写：可以直接测试 `services/` 中的函数，也可以使用 `TestClient` 测试 API 端点。

### 8. 平滑迁移，风险极低
- **你的原有代码（`agent/`、`rag/`、`chroma_db/` 等）一行都不用改**，只需在 `app/services/` 中写薄薄的 wrapper 调用它们。
- 旧的 `app.py`（Streamlit 入口）可以重命名保留，与 FastAPI 同时运行（不同端口），逐步过渡。

### 一个最直接的对比场景
| 之前 | 之后 |
|------|------|
| 只能通过命令行或 Streamlit 界面使用 | 任何客户端通过 HTTP 调用 |
| 无法被其他服务集成 | 可作为独立微服务被编排 |
| 无自动 API 文档 | Swagger UI 开箱即用 |
| 部署需要手动运行脚本 | `docker run` 一键启动 |
| 性能受限于 Streamlit 单线程 | 异步高并发，支持负载均衡 |

**总结**：封装成 FastAPI 并非只是“换个框架”，而是让你的 RAG+LangGraph Agent 从一个**脚本/工具**，进化为一个**企业级、可扩展、易协作的后端服务**。如果你需要我帮你把原来的 `agent` 模块中某个具体类（比如 `YourLangGraphAgent`）封装成 FastAPI 依赖的示例代码，请贴出关键片段，我可以直接为你写适配代码。

## 开源协议

MIT License
```
