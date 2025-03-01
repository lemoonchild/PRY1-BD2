import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
API_PORT = os.getenv("API_PORT")

# Construir la URL base completa
BASE_URL = f"{API_BASE_URL}:{API_PORT}"