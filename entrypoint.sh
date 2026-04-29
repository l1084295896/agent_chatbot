#!/bin/bash
# Entrypoint 脚本 - 容器启动入口
#
# 功能：
# 1. 检查向量库是否需要初始化
# 2. 如需初始化则运行 init_db.py
# 3. 启动 Streamlit 应用
#
# 说明：
# - 使用 MD5 去重机制，重复启动不会重复加载文档
# - 向量库持久化在 volumes 中，重启后无需重新初始化

set -e

echo "=========================================="
echo "智扫通机器人智能客服 - 启动脚本"
echo "=========================================="

# 检查向量库是否已初始化（通过检查 chroma.sqlite3 是否存在）
if [ ! -f "/app/chroma_db/chroma.sqlite3" ]; then
    echo "检测到向量库未初始化，正在初始化..."
    python init_db.py
    echo "向量库初始化完成"
else
    echo "向量库已存在，跳过初始化"
fi

echo "启动 Streamlit 应用..."
echo "=========================================="

# 启动 Streamlit
exec streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true
