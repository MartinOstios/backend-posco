#! /usr/bin/env bash

# Esperar hasta que inicie la DB
python /app/src/config/backend_pre_start.py

# Crear los datos iniciales en la DB
python /app/src/config/initial_data.py

# Inicializar el servidor
fastapi dev src/main.py --host 0.0.0.0