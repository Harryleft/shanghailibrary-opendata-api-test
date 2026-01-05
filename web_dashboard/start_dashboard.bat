@echo off
echo Starting Shanghai Library API Dashboard...
echo.
echo Dashboard will be available at: http://localhost:8888
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
python -m http.server 8888
