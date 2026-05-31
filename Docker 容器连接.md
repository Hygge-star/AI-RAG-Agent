## 在 Windows 上使用 Docker 部署FastAPI 项目

本文档记录了从 **安装 Linux 子系统** 到 **成功运行 Docker 容器** 的全过程

---

### 一、准备工作：开启 WSL 2（Windows Subsystem for Linux）

Docker Desktop 在 Windows 上推荐使用 WSL 2 作为后端，性能更好。

1. **以管理员身份打开 PowerShell**，执行：
   ```powershell
   # 启用 WSL 功能
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   # 启用虚拟机平台
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```

2. **重启电脑**。

3. **安装 WSL 2 更新包**：下载并运行 [wsl_update_x64.msi](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi)。

4. **将 WSL 2 设为默认版本**：
   ```powershell
   wsl --set-default-version 2
   ```

5. **安装 Linux 发行版**（以 Ubuntu 为例）：
   ```powershell
   wsl --install -d Ubuntu
   ```
   安装完成后启动 Ubuntu，设置用户名和密码。

---

### 二、安装 Docker Desktop

1. 从 [Docker 官网](https://www.docker.com/products/docker-desktop/) 下载 Docker Desktop for Windows。
2. 双击安装，**务必勾选 “Use WSL 2 instead of Hyper-V”**。
3. 安装完成后，**重启电脑**。
4. 启动 Docker Desktop（桌面图标或开始菜单），等待鲸鱼图标稳定。

---

### 三、配置 Docker 镜像加速器（国内用户必须）

1. 打开 Docker Desktop → **Settings** → **Docker Engine**。
2. 在 JSON 配置中添加以下内容（保留原有字段）：
   ```json
   {
     "registry-mirrors": [
       "https://docker.mirrors.ustc.edu.cn",
       "https://hub-mirror.c.163.com"
     ]
   }
   ```
3. 点击 **Apply & Restart**。

---

### 四、准备你的 FastAPI 项目

确保项目根目录有以下文件：

```
项目根目录/
├── main.py                 # FastAPI 入口
├── agent/                  # 你的 ReactAgent 代码
├── model/                  # 模型工厂等
├── frontend/
│   └── dist/
│       └── index.html      # 前端页面
├── requirements.txt        # 精简后的依赖列表
├── Dockerfile              # 镜像构建脚本
└── .dockerignore           # 忽略文件（可选）
```

**精简 requirements.txt 示例**（只保留真正需要的）：
```
fastapi==0.135.2
uvicorn[standard]==0.41.0
python-dotenv==1.2.2
langchain==1.2.13
langchain-community==0.4.1
chromadb==1.5.5
tiktoken==0.12.0
openai==2.26.0
dashscope==1.25.13
```

---

### 五、编写 Dockerfile

在项目根目录创建 `Dockerfile`（内容根据你的项目调整）：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（如有需要）
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 六、构建 Docker 镜像

在项目根目录打开 PowerShell（或 WSL 终端），执行：

```bash
docker build -t knowledge-assistant .
```
---

### 七、运行容器

#### 基础运行（不带环境变量）
```bash
docker run -d --name my-assistant -p 8000:8000 knowledge-assistant
```

#### 带环境变量（如 API 密钥）
```bash
docker run -d --name my-assistant -p 8000:8000 -e DASHSCOPE_API_KEY="你的阿里云密钥" knowledge-assistant
```

#### 使用 .env 文件（推荐）
创建 `.env` 文件：
```
DASHSCOPE_API_KEY=你的密钥
```
然后运行：
```bash
docker run -d --name my-assistant -p 8000:8000 --env-file .env knowledge-assistant
```

---

### 八、验证与调试

- **查看容器状态**：`docker ps`
- **查看日志**：`docker logs my-assistant`
- **进入容器内部**：`docker exec -it my-assistant bash`
- **测试 API**：在浏览器打开 `http://localhost:8000`，应该看到前端页面。发送问题测试。

---

### 九、常见问题与解决

| 问题 | 原因 | 解决 |
|------|------|------|
| `docker: command not found` | Docker 未安装或未启动 | 安装 Docker Desktop 并启动 |
| `no such host` / 拉取镜像慢 | 网络问题或镜像加速器未配置 | 配置国内镜像加速器 |
| `pip install` 失败 | 网络或依赖版本问题 | 使用国内 pip 源，精简 requirements.txt |
| 容器启动后立即退出 | 缺少环境变量或代码错误 | `docker logs` 查看错误，补充环境变量 |
| 端口被占用 | 8000 端口已被其他程序使用 | 更换映射端口，如 `-p 8080:8000` |

---

### 十、总结

1. **在 Windows 上配置 WSL 2 和 Docker Desktop**。
2. **编写 Dockerfile 将 Python 项目容器化**。
3. **构建镜像、运行容器、管理环境变量**。
4. **使用 `docker logs` 和 `docker exec` 调试**。
5. **解决国内网络下的镜像拉取和依赖安装问题**。

### 十一、常用 Docker 命令

#### 1. 构建镜像
```bash
docker build -t knowledge-assistant .
```
- `-t`：给镜像起个名字（tag），方便后续引用。
- `.`：构建上下文（当前目录），Docker 会寻找 `Dockerfile`。

#### 2. 运行容器
```bash
docker run -d --name my-assistant -p 8000:8000 -e DASHSCOPE_API_KEY="你的密钥" knowledge-assistant
```
- `-d`：后台运行（detach）。
- `--name`：给容器起个好记的名字。
- `-p 宿主机端口:容器端口`：访问 `localhost:8000` 就等于访问容器内的 8000 端口。
- `-e KEY=value`：设置环境变量（可多次使用）。
- 最后是镜像名。

#### 3. 查看运行中的容器
```bash
docker ps
```
只显示正在运行的容器。加 `-a` 显示所有（包括已停止的）。

#### 4. 查看容器日志
```bash
docker logs my-assistant
```
如果容器启动失败或运行时报错，日志是排查的第一手资料。加 `-f` 可以实时跟踪（类似 `tail -f`）。

#### 5. 停止容器
```bash
docker stop my-assistant
```

#### 6. 删除容器（必须先停止）
```bash
docker rm my-assistant
```

#### 7. 进入容器内部调试（重要！）
```bash
docker exec -it my-assistant bash
```
- `-it`：交互式终端。
- `bash`：启动 shell。如果容器是精简版没有 bash，可以试试 `sh`。

进去之后可以：
- 查看环境变量：`echo $DASHSCOPE_API_KEY`
- 测试网络：`curl localhost:8000/api/health`
- 查看代码：`ls /app`
- 退出：输入 `exit`

#### 8. 删除镜像
```bash
docker rmi knowledge-assistant
```
要先删除依赖该镜像的所有容器（`docker rm`）。

---

### 十二、连接容器的本质（为什么这样配置）

FastAPI 服务监听在容器内部的 `0.0.0.0:8000`。但是容器有自己的网络命名空间，电脑（宿主机）不能直接访问它。**端口映射** `-p 8000:8000` 在宿主机和容器之间建立了一条通道：

```
浏览器访问 http://localhost:8000
    ↓
宿主机网络栈收到请求，发现 8000 端口被映射
    ↓
转发到容器内部的 8000 端口
    ↓
FastAPI 处理请求并返回
```
---

### 十三、项目中遇到的问题与解决方法

#### Q1：容器启动后立即退出，日志显示 `DASHSCOPE_API_KEY` 找不到。
**原因**：代码需要阿里云通义千问的 API 密钥，但容器中没有这个环境变量。  
**解决**：运行时加上 `-e DASHSCOPE_API_KEY="你的密钥"`，或使用 `--env-file .env`。

#### Q2：`docker run` 报端口已被占用（`bind: address already in use`）。
**原因**：宿主机 8000 端口已经被其他程序（比如本地直接运行的 FastAPI）占用了。  
**解决**：换个端口，比如 `-p 8080:8000`，然后访问 `localhost:8080`。

#### Q3：构建镜像时 `pip install` 很慢或失败。
**原因**：默认从国外 PyPI 下载，网络不稳定；或者 `requirements.txt` 包含不兼容的包（如 `torch==2.9.0+cu126`）。  
**解决**：
- 在 Dockerfile 中使用国内镜像：`-i https://pypi.tuna.tsinghua.edu.cn/simple`
- 精简 `requirements.txt`，只保留项目真正需要的包，去掉 `+cu126` 等特殊后缀。

#### Q4：前端页面能打开，但提问后没有回答。
**可能原因**：
1. 后端 API 报错（`docker logs my-assistant` 查看）。
2. 环境变量缺失（如 `DASHSCOPE_API_KEY` 未设置）。
3. 容器内无法访问外网（如调用 OpenAI API 需要代理）。  
**排查**：进入容器 `docker exec -it my-assistant bash`，手动 `curl` 测试或 `python` 导入模块看错误。

---

### 十四、一句话总结

> “Docker 容器通过端口映射对外提供服务，通过环境变量传递配置，通过日志和 `exec` 命令进行调试。我把 FastAPI 应用打包成镜像，运行容器时映射 8000 端口，并传入 API 密钥，最终在浏览器访问 `localhost:8000` 就能正常使用。”

---
