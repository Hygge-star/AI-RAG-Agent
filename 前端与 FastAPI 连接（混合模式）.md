## 前端与 FastAPI 连接详解（混合模式）—— 适配你的“智能知识库助手”项目

本文档将**逐步骤**解释前端（`index.html`）如何与 FastAPI 后端连接，以及每一步背后的设计原因。

---

### 1. 为什么选择“混合模式”？

**项目情况**：有一个 FastAPI 后端（提供 RAG 问答 API），并希望有一个简洁的 Web 对话界面。不想分离部署前后端（即不需要单独开一个 Node 服务器或 Nginx 托管前端）。

**混合模式定义**：后端 FastAPI 既提供 API 接口，又通过静态文件托管（`StaticFiles`）和兜底路由（`/{full_path:path}`）来直接返回前端 HTML/CSS/JS 文件。

**选择它的原因**：
- **部署简单**：只需运行一个 FastAPI 服务，前后端统一端口（如 8000），无需配置 Nginx 或处理跨域。
- **开发效率**：前端页面可以直接放在 `frontend/dist` 目录中，后端修改后刷新浏览器即可看到变化（配合 `--reload`）。
- **支持 SPA 路由**：通过兜底路由，用户在浏览器刷新 `/about` 等前端路由时不会看到 404，而是正确返回 `index.html`，由前端路由接管。

---

### 2. 整体交互流程

```
浏览器访问 http://localhost:8000
        │
        ▼
FastAPI 根路由 "/" 返回 frontend/dist/index.html
        │
        ▼
浏览器加载 index.html，执行其中的 JavaScript
        │
        ▼
用户在输入框提问，JS 发送 POST 请求到 /api/v1/webchat
        │
        ▼
FastAPI 路由匹配到 /api/v1/webchat，调用 chat.py 中的 web_chat 函数
        │
        ▼
后端调用 ReactAgent 进行 RAG 检索 + LLM 生成，返回 JSON { "answer": "..." }
        │
        ▼
前端 JS 接收答案，动态显示在页面上
```

---

### 3. 后端配置步骤及原因

#### 3.1 挂载静态文件目录 —— `main.py` 中的 `app.mount`

```python
FRONTEND_ROOT = "./frontend/dist"
assets_path = os.path.join(FRONTEND_ROOT, "assets")
if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
```

**为什么这样做？**
- 前端构建产物（如 Vite 生成的 `index.html` 和 `assets/index-abc123.js`）需要被浏览器访问。浏览器请求 `/assets/index-abc123.js` 时，FastAPI 必须能找到该文件并返回。
- `StaticFiles` 专门用于托管静态文件，它会自动处理缓存头、MIME 类型等，性能好且安全。
- 仅挂载 `assets` 目录，而不是整个 `frontend/dist`，是为了避免意外暴露源码或配置文件。`index.html` 本身不通过 `StaticFiles` 托管，而是通过后面的 `FileResponse` 返回。

#### 3.2 根路由返回 `index.html` —— `main.py` 中的 `@app.get("/")`

```python
@app.get("/")
async def root():
    index_path = os.path.join(FRONTEND_ROOT, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not found"}
```

**为什么这样做？**
- 当用户访问 `http://localhost:8000` 时，期望看到的是聊天界面，而不是后端 API 的 JSON 消息。
- `FileResponse` 会将文件内容以正确的 `Content-Type`（text/html）发送给浏览器，浏览器解析 HTML 并渲染页面。
- 如果 `index.html` 不存在，则返回提示信息，方便调试。

#### 3.3 兜底路由支持前端路由 —— `main.py` 中的 `@app.get("/{full_path:path}")`

```python
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api/"):
        return {"detail": "Not Found"}, 404
    file_path = os.path.join(FRONTEND_ROOT, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(FRONTEND_ROOT, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Not Found"}, 404
```

**为什么这样做？**
- 前端是一个单页应用（SPA），它可能使用前端路由，例如 `/about` 或 `/chat/history`。当用户在浏览器直接访问这些路径或刷新页面时，浏览器会向 FastAPI 请求 `/about`。
- 如果没有兜底路由，FastAPI 找不到 `/about` 对应的路由，就会返回 404。但正确的行为应该是：返回 `index.html`，让前端 JavaScript 读取当前 URL 并渲染对应组件。
- 兜底路由放在所有 API 路由**之后**，确保 `/api/...` 请求优先被 API 路由处理，不会被兜底路由拦截。
- 同时，如果请求的路径确实对应一个物理文件（如 `/assets/logo.png`），则直接返回该文件，而不是返回 `index.html`。

#### 3.4 提供 API 端点 —— `chat.py` 中的 `/webchat`

```python
@router.post("/webchat", response_model=WebChatResponse)
async def web_chat(request: WebChatRequest, rag_service=Depends(get_rag_service)):
    reply = rag_service.rag_summarize(request.question)
    return WebChatResponse(answer=reply)
```

**为什么这样设计？**
- 前端需要发送 `{"question": "..."}` 并接收 `{"answer": "..."}`，格式简单明了。
- 原有 `/chat` 端点使用 `message` 和 `session_id` 字段，那是为其他客户端（如移动 App）设计的，为了保持兼容性，新增 `/webchat` 端点专门为 Web 前端服务。
- 通过依赖注入 `Depends(get_rag_service)`，可以复用同一个 `ReactAgent` 实例，避免重复初始化向量数据库和 LLM 连接。

#### 3.5 CORS 中间件 —— 即使同源也添加

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**为什么这样做？**
- 虽然在混合模式下前后端同源（都是 `localhost:8000`），不会触发浏览器 CORS 限制，但添加 CORS 中间件有两个好处：
  1. 方便调试：如果你临时用 `npm run dev` 单独启动前端（例如端口 5173）来热更新，此时不同端口需要 CORS。
  2. 未来扩展：如果你要将前端部署到 CDN（如 `https://example.com`），后端部署到 `https://api.example.com`，CORS 配置已就绪。

---

### 4. 前端配置步骤及原因

#### 4.1 发送 HTTP 请求 —— `index.html` 中的 `fetch`

```javascript
const API_URL = '/api/v1/webchat';

async function sendQuestion(question) {
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question })
    });
    const data = await response.json();
    return data.answer;
}
```

**为什么这样做？**
- 使用相对路径 `/api/v1/webchat`，因为前后端同源，浏览器会自动补全为 `http://localhost:8000/api/v1/webchat`。
- 设置 `Content-Type: application/json` 告诉后端请求体是 JSON 格式。
- 后端返回的 JSON 中 `answer` 字段就是助手的回答，直接取出显示。

#### 4.2 处理用户输入和显示回答

```javascript
// 添加用户消息
addMessage('user', question);
// 显示加载动画
showTyping();
// 发送请求并等待回答
const answer = await sendQuestion(question);
hideTyping();
addMessage('assistant', answer);
```

**为什么这样做？**
- 提供即时反馈：用户点击发送后立即在界面上显示自己的问题，同时显示“正在输入”动画，避免用户焦虑等待。
- 异步请求不阻塞 UI，用户体验流畅。

#### 4.3 自动滚动和输入框自适应

```javascript
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
// 每次添加新消息后调用 scrollToBottom()
```

**为什么这样做？**
- 对话通常从上到下排列，用户希望最新消息始终可见。自动滚动到底部避免了手动滚动。

#### 4.4 错误处理

```javascript
try {
    const response = await fetch(...);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    // ...
} catch (err) {
    showError('网络或服务异常，请稍后重试');
    addMessage('assistant', `❌ 出错啦：${err.message}`);
}
```

**为什么这样做？**
- 网络请求可能失败（后端挂掉、超时等），友好的错误提示比静默失败或控制台报错更能帮助用户。
- 在对话中显示一条错误消息，让用户知道当前操作未成功。

---

### 5. 开发与调试时的关键注意点（

| 可能遇到的问题 | 原因 | 解决方案 |
|--------------|------|----------|
| 访问 `http://localhost:8000` 看到 `{"message":"Frontend not found"}` | `FRONTEND_ROOT` 路径不正确，或 `frontend/dist/index.html` 不存在。 | 检查 `main.py` 中的 `FRONTEND_ROOT = "./frontend/dist"` 是否为相对路径，确保该目录下存在 `index.html`。 |
| 发送消息后控制台报 `404 Not Found` | 前端请求的 URL 与后端路由不匹配。 | 确认 `index.html` 中 `API_URL` 是 `/api/v1/webchat`，而后端 `chat.py` 中有 `@router.post("/webchat")` 且路由注册前缀为 `/api/v1`。 |
| 刷新 `/some-route` 页面显示 `{"detail":"Not Found"}` | 兜底路由未正确实现或放在 API 路由之前。 | 检查 `main.py` 中 `@app.get("/{full_path:path}")` 是否在所有 `app.include_router` 之后，且没有提前 return。 |
| 前端页面加载但样式/JS 缺失 | 静态资源路径错误，例如 `index.html` 中引用 `./assets/index.js` 但后端挂载的是 `/assets`。 | 前端构建时确保资源引用使用绝对路径（以 `/` 开头）。Vite 中配置 `base: '/'`。 |
| 后端打印 `收到消息` 但没有回答 | `ReactAgent` 内部 RAG 流程出错或 LLM API 密钥未设置。 | 检查 `rag_wrapper.py` 中的日志输出，确保环境变量 `OPENAI_API_KEY` 已设置。 |

---

### 6. 总结：每一步的“为什么”一句话版

| 步骤 | 为什么 |
|------|--------|
| 挂载 `/assets` 静态目录 | 让浏览器能下载 JS/CSS/图片等资源 |
| 根路由返回 `index.html` | 用户访问根路径时看到聊天界面，而非 JSON |
| 兜底路由返回 `index.html` | 支持前端路由（刷新页面不 404） |
| 提供 `/api/v1/webchat` 端点 | 前端用简单的 `{question}` 格式获取 `{answer}` |
| 前端使用相对路径 `/api/v1/webchat` | 前后端同源，无需配置跨域或完整 URL |
| 发送请求时显示加载动画 | 提升用户体验，提示“正在思考” |
| 自动滚动到底部 | 让用户始终看到最新对话 |
| 错误处理和重试提示 | 网络失败时给予明确反馈 |
