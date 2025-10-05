"""
Hackstronauts - Sistema de Análisis de Asteroides
Punto de entrada principal del sistema sin Docker
"""

import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar variables de entorno para Render
try:
    from setup_env import setup_render_env
    setup_render_env()
except ImportError:
    pass  # No es crítico si no se puede importar

# Importar componentes del sistema
from src.api.routes import router as api_router
from src.api.routes.explanation_routes import explanation_router
from src.database.postgres_connector import PostgreSQLConnector
from src.supervisors.hybrid_supervisor import HybridSupervisor

# Configuración de la aplicación
app = FastAPI(
    title="Hackstronauts API",
    description="Sistema de análisis de asteroides con agentes de IA",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales para el sistema
db_connector = None
supervisor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación."""
    global db_connector, supervisor
    
    print("🚀 Iniciando Hackstronauts...")
    
    # Inicializar base de datos
    try:
        db_connector = PostgreSQLConnector()
        print("✅ Base de datos conectada")
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        db_connector = None
    
    # Inicializar supervisor
    try:
        supervisor = HybridSupervisor()
        print("✅ Supervisor híbrido inicializado")
    except Exception as e:
        print(f"❌ Error inicializando supervisor: {e}")
        supervisor = None
    
    print("🎯 Sistema listo para recibir peticiones")
    
    yield
    
    # Cleanup al cerrar
    print("🛑 Cerrando Hackstronauts...")
    if db_connector:
        try:
            await db_connector.close()
        except:
            pass  # Ignorar errores de cierre

# Asignar lifespan a la app
app.router.lifespan_context = lifespan

# Incluir rutas de la API
app.include_router(api_router, prefix="/api/v1")
app.include_router(explanation_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Endpoint raíz con información del sistema."""
    return {
        "message": "Hackstronauts API - Sistema de Análisis de Asteroides",
        "version": "1.0.0",
        "status": "active",
        "database": "connected" if db_connector else "disconnected",
        "supervisor": "active" if supervisor else "inactive"
    }

@app.get("/health")
async def health_check():
    """Endpoint de salud del sistema."""
    return {
        "status": "healthy",
        "database": "connected" if db_connector else "disconnected",
        "supervisor": "active" if supervisor else "inactive"
    }

def start_system():
    """Función para iniciar el sistema."""
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"🌐 Iniciando servidor en http://{host}:{port}")
    print(f"🔧 Modo debug: {debug}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

if __name__ == "__main__":
    start_system()
