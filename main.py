"""
Hackstronauts - Sistema de Análisis de Asteroides
Punto de entrada principal del sistema
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Crear la aplicación FastAPI
app = FastAPI(
    title="Hackstronauts API",
    description="Sistema de análisis de asteroides con agentes de IA",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raíz con información del sistema."""
    return {
        "message": "Hackstronauts API - Sistema de Análisis de Asteroides",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Endpoint de salud del sistema."""
    return {
        "status": "healthy",
        "message": "Sistema funcionando correctamente"
    }

if __name__ == "__main__":
    print("🚀 Iniciando Hackstronauts...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
