#!/bin/bash
cd /home/ubuntu/posco/backend
source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:/home/ubuntu/posco/backend
# Inicializa la base de datos
python src/config/backend_pre_start.py
python src/config/initial_data.py
# Inicia el servidor
exec uvicorn src.main:app --host 0.0.0.0 --port 8000