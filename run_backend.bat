@echo off
cd backend
venv\Scripts\python -m uvicorn main:app --reload --port 8045
pause
