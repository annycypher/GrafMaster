@echo off
rem GrafMaster Web — запуск локальной веб-версии и открытие в браузере.
rem Если приложение уже запущено, просто откроется вкладка браузера.
start "" "C:\Users\Anna\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run "%~dp0..\web_app.py" --server.headless true --server.port 8501 --browser.gatherUsageStats false
timeout /t 7 /nobreak >nul
start "" "http://127.0.0.1:8501"
