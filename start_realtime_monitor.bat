@echo off
echo ========================================
echo 上海图书馆开放数据API - 实时监控服务器
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo 虚拟环境未找到，请先创建虚拟环境
    echo python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install requirements if needed
echo 检查依赖...
pip show flask-sock >nul 2>&1
if errorlevel 1 (
    echo 安装实时监控依赖...
    pip install -r requirements_realtime.txt
)

REM Check API key
echo.
echo 检查API Key...
if not defined SHANGHAI_LIBRARY_API_KEY (
    echo 警告: SHANGHAI_LIBRARY_API_KEY 环境变量未设置
    echo 请设置API Key: set SHANGHAI_LIBRARY_API_KEY=your_key_here
    echo 或在 config.py 中配置
    echo.
)

REM Start the server
echo.
echo 启动实时监控服务器...
echo 仪表板地址: http://localhost:5000
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

python realtime_server.py

pause
