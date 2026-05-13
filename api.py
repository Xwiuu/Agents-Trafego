from fastapi import FastAPI
from interfaces.routes import app
from dotenv import load_dotenv

# Carrega variáveis de ambiente globalmente
load_dotenv()

# Este arquivo é o ponto de entrada principal para a API.
# Ele importa a configuração modular de interfaces/routes.py

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
