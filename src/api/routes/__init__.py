"""
API Routes - Rutas de la API REST
Combina todos los routers en un router principal
"""

from fastapi import APIRouter

# Importar todos los routers individuales
from .analysis_routes import analysis_router
from .explanation_routes import explanation_router
from .ingestor_routes import ingestor_router
from .metrics_routes import metrics_router
from .ml_prediction_routes import ml_prediction_router
from .nasa_routes import nasa_router
from .neo_routes import neo_router
from .simulation_nasa_routes import simulation_nasa_router
from .simulation_routes import simulation_router
from .visualization_routes import visualization_router

# Crear el router principal
router = APIRouter()

# Incluir todos los routers con sus prefijos
router.include_router(analysis_router, prefix="/analysis", tags=["Análisis"])
router.include_router(explanation_router, prefix="/explanation", tags=["Explicaciones"])
router.include_router(ingestor_router, prefix="/ingestor", tags=["Ingestor de Datos"])
router.include_router(metrics_router, prefix="/metrics", tags=["Métricas"])
router.include_router(ml_prediction_router, prefix="/ml-predictions", tags=["Predicciones ML"])
router.include_router(nasa_router, prefix="/nasa", tags=["NASA API"])
router.include_router(neo_router, prefix="/neo", tags=["NEOs"])
router.include_router(simulation_nasa_router, prefix="/simulation-nasa", tags=["Simulación NASA"])
router.include_router(simulation_router, prefix="/simulation", tags=["Simulación"])
router.include_router(visualization_router, prefix="/visualization", tags=["Visualización"])

__all__ = ["router"]
