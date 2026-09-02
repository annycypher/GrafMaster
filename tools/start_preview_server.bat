@echo off
rem Запуск локального сервера предпросмотра GrafMaster (макеты и галерея).
rem После запуска откройте: http://127.0.0.1:8899/UI_MOCKUPS.html
start "" "C:\Users\Anna\AppData\Local\Programs\Python\Python312\pythonw.exe" "%~dp0serve_docs.py"
