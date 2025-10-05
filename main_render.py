"""
Hackstronauts - Versión simplificada para Render
Solo las funcionalidades básicas sin dependencias complejas
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

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
        "status": "active",
        "deployment": "render"
    }

@app.get("/health")
async def health_check():
    """Endpoint de salud del sistema."""
    return {
        "status": "healthy",
        "deployment": "render",
        "message": "Sistema funcionando en Render"
    }

@app.get("/api/v1/explain/simulate/{neo_id}")
async def simulate_asteroid_simple(neo_id: str, level: str = "basic"):
    """
    Simulación simplificada de asteroide
    """
    return {
        "asteroid_id": neo_id,
        "level": level,
        "simulation_results": {
            "status": "completed",
            "asteroid_data": {
                "id": neo_id,
                "name": f"Asteroid {neo_id}",
                "diameter_min": 16.84,
                "is_potentially_hazardous": False
            },
            "explanation_data": {
                "results": {
                    "risk_summary": {
                        "overall_risk": "Muy Bajo - Monitoreo básico",
                        "recommendations": ["Continuar monitoreo rutinario"],
                        "monitoring_priority": "Baja - Monitoreo mensual"
                    }
                }
            },
            "ml_predictions": {
                "trajectory_prediction": "Predicción de trayectoria basada en ML",
                "confidence_score": 0.85,
                "status": "success"
            }
        },
        "report_metadata": {
            "generated_at": "2024-10-05T12:00:00Z",
            "level": level,
            "version": "1.0",
            "simulation_type": "simplified"
        }
    }

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"🌐 Iniciando servidor en http://{host}:{port}")
    
    uvicorn.run(
        "main_render:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
