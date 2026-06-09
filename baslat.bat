@echo off
echo  Smart Kitchen Assistant 

call venv\Scripts\activate.bat

start "Backend" cmd /k "cd Backend && uvicorn main:app --reload"

start "Frontend" cmd /k "cd Frontend && streamlit run Home.py"