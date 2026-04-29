# 智扫通机器人智能客服

基于 RAG（检索增强生成）的扫地机器人智能客服系统。

## 项目简介

智扫通是一个面向扫地机器人和扫拖一体机场景的中文智能客服系统，基于 LangChain + ChromaDB + Streamlit 构建，支持：

- 专业知识问答（RAG 检索）
- 天气相关保养建议
- 个人使用报告查询
- 智能对话式交互

## 技术栈

- **前端**: Streamlit
- **LLM**: 阿里通义千问 (Qwen3-max)
- **向量数据库**: ChromaDB
- **Embedding**: DashScope text-embedding-v3
- **框架**: LangChain

## 项目结构

```
.
├── agent/                 # Agent 核心模块
│   ├── react_agent.py    # ReAct Agent 实现
│   └── tools/            # 工具函数
├── chroma_db/            # Chroma 向量库持久化目录
├── config/               # 配置文件
├── data/                 # 数据目录
│   └── external/         # 用户使用记录（CSV）
├── logs/                 # 日志目录
├── model/                # 模型工厂
├── prompts/              # 提示词模板
├── rag/                  # RAG 服务
├── utils/                # 工具函数
├── app.py               # Streamlit 应用入口
├── init_db.py           # 知识库初始化脚本
├── entrypoint.sh        # Docker 启动脚本
└── requirements.txt     # Python 依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

确保已设置 DashScope API Key：

```bash
export DASHSCOPE_API_KEY="your-api-key"
```

### 3. 初始化知识库（首次部署）

```bash
python init_db.py
```

此步骤将 `data/external/` 目录下的文档加载到 Chroma 向量库。后续添加新文档后也需重新运行此步骤。

### 4. 启动应用

```bash
streamlit run app.py
```

## 知识库更新

当需要更新知识库内容时：

1. 将新的 TXT/PDF 文档放入 `data/` 目录（**不是 data/external/**）
2. 重新运行初始化脚本：

```bash
python init_db.py
```

脚本会自动跳过已加载的文档（通过 MD5 去重），仅加载新增或修改的文档。

## Docker 部署

### 构建并启动

```bash
docker-compose up -d
```

首次启动会自动初始化向量库，后续启动会自动跳过已初始化的状态。

### 查看日志

```bash
docker-compose logs -f
```

### 停止服务

```bash
docker-compose down
```

## 配置说明

配置文件位于 `config/` 目录：

- `agent.yml`: Agent 相关配置
- `chromadb.yml`: ChromaDB 配置
- `prompt.yml`: 提示词配置
- `rag.yml`: RAG 和模型配置

## 知识库数据

将扫地机器人相关的知识文档放入 `data/` 目录（**不是 data/external/**），支持格式：

- TXT 文本文件
- PDF 文档

> 注意：`data/external/` 目录用于存放用户使用记录（CSV），不是知识库文档目录。

## License

MIT
