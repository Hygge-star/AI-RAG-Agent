# Streamlit 应用部署记录
项目名称：AI-RAG-Agent
部署时间：2026年3月25日
部署平台：Streamlit Community Cloud

本文档记录了将项目成功部署到 Streamlit Cloud 的全过程，包括环境配置、Git 版本控制、依赖问题解决、代码修正以及访问控制设置。希望对后续维护和分享有所帮助。

## 1. 环境准备
### 1.1 本地环境
操作系统：Windows

Python 版本：3.13.5（本地开发）

虚拟环境：推荐使用 venv 隔离依赖

项目入口：app.py

### 1.2 远程仓库
GitHub 仓库：git@github.com:Hygge-star/AI-RAG-Agent-.git

默认分支：master

## 2. Git 版本控制与推送
### 2.1 初始化本地仓库并提交
powershell
git init
git add .
git commit -m "init"
### 2.2 关联远程仓库
powershell
git remote add origin git@github.com:Hygge-star/AI-RAG-Agent-.git
### 2.3 推送遇到问题及解决
|错误信息|原因|解决方案|
| ---- | ---- | ---- |
|fatal: not a git repository 或 Nothing specified, nothing added.|git add 未指定路径|使用 git add . 添加所有文件|
|error: src refspec main does not match any|本地分支为 master，推送目标为 main|使用 git push -u origin master|
|ssh: connect to host github.com port 22: Connection refused|SSH 端口被阻断或密钥未配置|改用 HTTPS 地址：git remote set - url origin https://github.com/Hygge - star/AI - RAG - Agent.git|
最终成功推送命令：

**powershell**
git push -u origin master
3. 依赖安装与问题处理
3.1 依赖文件 requirements.txt
在本地虚拟环境中生成：

**powershell**
pip freeze > requirements.txt
3.2 遇到的依赖问题
问题1：ModuleNotFoundError: No module named 'aiohttp'
原因：requirements.txt 中缺少 aiohttp

解决：

**powershell**
pip install aiohttp
pip freeze > requirements.txt
问题2：torch==2.9.0+cu126 无法安装
错误：ERROR: No matching distribution found for torch==2.9.0+cu126

原因：带 +cu126 后缀的版本不在 PyPI 官方源中

解决：修改 requirements.txt，将 torch==2.9.0+cu126 改为 torch==2.9.0，同样处理 torchvision

问题3：Python 版本兼容性
现象：某些包在 Python 3.14 上安装失败

解决：在项目根目录创建 runtime.txt，指定 Python 3.12：

text
python-3.12
3.3 最终依赖清单
确保 requirements.txt 包含以下关键包（示例）：

text
aiohttp==3.13.3
langchain==1.2.13
langchain-community==0.4.1
torch==2.9.0
torchvision==0.24.0
streamlit==1.55.0
...
## 4. Streamlit Cloud 部署配置
4.1 创建应用
登录 Streamlit Cloud

点击 "New app"

选择仓库 Hygge-star/AI-RAG-Agent-，分支 master，主文件 app.py

点击 Deploy

### 4.2 设置 Secrets（API 密钥）
阿里云 DashScope API Key 必须通过 Secrets 安全存储：

在应用管理页面 → Secrets → 添加键值对：

Key：DASHSCOPE_API_KEY

Value：你的 DashScope API Key（直接粘贴，不加引号）

如果使用 TOML 格式编辑器，则填写：

toml
DASHSCOPE_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
### 4.3 访问控制（可选）
为防止 API 额度被滥用，将应用设置为 "Only specific people can view this app"，并仅邀请测试人员的邮箱：

应用设置 → Who can view this app → 选择 Only specific people → 输入受邀者邮箱

## 5. 代码修正
### 5.1 错误：ValidationError: Did not find dashscope_api_key
位置：model/factory.py 中的 generator 方法

原因：ChatTongyi 初始化时未正确传递 API 密钥参数名

修改后代码：

python
import os
from langchain_community.chat_models import ChatTongyi

class ChatModelFactory(BaseModelFactory):
    def generator(self):
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY environment variable is not set.")
        return ChatTongyi(
            model=rag_conf["chat_model_name"],
            dashscope_api_key=api_key      # 注意参数名是 dashscope_api_key
        )
### 5.2 其他检查
确保 config/rag.yml 中的 chat_model_name 是有效模型（如 qwen-plus）

提交所有修改并推送到 GitHub：

powershell
git add model/factory.py requirements.txt runtime.txt
git commit -m "Fix API key param and dependencies"
git push origin master
## 6. 最终部署结果
应用成功启动，日志中无错误

访问地址：https://fwd23qczvmgzz7ftpxr9lc.streamlit.app/

访问控制生效，仅受邀用户可见

## 7. 经验总结
|阶段|常见问题|解决方案|
| ---- | ---- | ---- |
|Git 推送|分支名不匹配、SSH 连接失败|使用正确的分支名，必要时改用 HTTPS|
|依赖管理|特定版本不存在、Python 版本不兼容|使用普通版本号，添加 runtime.txt 指定 Python|
|环境变量|API Key 缺失|通过 Streamlit Secrets 安全配置|
|代码参数|参数名错误|查阅库文档，使用正确的参数名（如 dashscope_api_key）|
|安全|API 额度被滥用|设置应用私密访问或邀请特定用户|
## 8. 相关文件
requirements.txt - 项目依赖

runtime.txt - 指定 Python 版本（python-3.12）

model/factory.py - 修正后的模型工厂

config/rag.yml - 配置文件（需包含 chat_model_name）

DEPLOYMENT.md - 本文档

记录完毕。
