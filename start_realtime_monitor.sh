#!/bin/bash

echo "========================================"
echo "上海图书馆开放数据API - 实时监控服务器"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -f ".venv/bin/activate" ]; then
    echo "虚拟环境未找到，请先创建虚拟环境"
    echo "python3 -m venv .venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements if needed
echo "检查依赖..."
pip show flask-sock > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "安装实时监控依赖..."
    pip install -r requirements_realtime.txt
fi

# Check API key
echo ""
echo "检查API Key..."
if [ -z "$SHANGHAI_LIBRARY_API_KEY" ]; then
    echo "警告: SHANGHAI_LIBRARY_API_KEY 环境变量未设置"
    echo "请设置API Key: export SHANGHAI_LIBRARY_API_KEY=your_key_here"
    echo "或在 config.py 中配置"
    echo ""
fi

# Start the server
echo ""
echo "启动实时监控服务器..."
echo "仪表板地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务器"
echo "========================================"
echo ""

python realtime_server.py
