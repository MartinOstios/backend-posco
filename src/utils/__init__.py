# Inicialización del paquete utils

# Exportar las funciones necesarias para que estén disponibles cuando se importa desde src.utils
import sys
from pathlib import Path
import importlib.util

# Ruta al archivo utils.py principal
utils_path = Path(__file__).parent.parent / "utils.py"

# Cargar el módulo utils.py
spec = importlib.util.spec_from_file_location("utils_main", utils_path)
utils_main = importlib.util.module_from_spec(spec)
sys.modules["utils_main"] = utils_main
spec.loader.exec_module(utils_main)

# Importar las funciones necesarias
generate_password_reset_token = utils_main.generate_password_reset_token
generate_reset_password_email = utils_main.generate_reset_password_email
send_email = utils_main.send_email
verify_password_reset_token = utils_main.verify_password_reset_token
generate_test_email = utils_main.generate_test_email
generate_new_account_email = utils_main.generate_new_account_email
EmailData = utils_main.EmailData
oauth_refresh_access_token = utils_main.oauth_refresh_access_token

__all__ = [
    "generate_password_reset_token",
    "generate_reset_password_email",
    "send_email",
    "verify_password_reset_token",
    "generate_test_email",
    "generate_new_account_email",
    "EmailData",
    "oauth_refresh_access_token",
] 