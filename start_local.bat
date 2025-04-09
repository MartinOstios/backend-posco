@echo off
call venv\Scripts\activate.bat

echo Iniciando servicios de backend...

:: Configurar PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%CD%

:: Esperar hasta que inicie la DB
python src/config/backend_pre_start.py

:: Crear los datos iniciales en la DB
python src/config/initial_data.py

:: Iniciar el servidor
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 