"""
Rutas para Explicaciones Científicas
Maneja las peticiones HTTP para generar explicaciones comprensibles
"""

from fastapi import APIRouter, HTTPException, Path
from typing import Optional

from ..controllers.explanation_controller import ExplanationController
from ..models.explanation_models import (
    CompleteExplanationResponse,
    AsteroidBasicResponse,
    ImpactExplanationResponse,
    TrajectoryExplanationResponse,
    MitigationExplanationResponse,
    RiskOverviewResponse
)

# Crear el router para explicaciones
explanation_router = APIRouter(prefix="/explain", tags=["Explicaciones"])

# Instancia del controlador (se inicializa solo cuando se necesita)
def get_explanation_controller():
    """Obtiene una instancia del controlador de explicaciones"""
    return ExplanationController()

@explanation_router.get("/asteroid/{neo_id}", response_model=CompleteExplanationResponse)
async def get_complete_explanation(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera explicación completa del asteroide
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Explicación completa con todos los análisis científicos
    """
    try:
        controller = get_explanation_controller()
        result = controller.get_complete_explanation(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando explicación completa: {str(e)}")

@explanation_router.get("/asteroid/{neo_id}/basics", response_model=AsteroidBasicResponse)
async def get_asteroid_basics(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera explicación básica del asteroide
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Explicación básica con tamaño, peligro y clasificación
    """
    try:
        controller = get_explanation_controller()
        result = controller.get_asteroid_basic_explanation(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando explicación básica: {str(e)}")

@explanation_router.get("/asteroid/{neo_id}/impact", response_model=ImpactExplanationResponse)
async def get_impact_explanation(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera explicación de efectos de impacto
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Explicación de impacto con comparaciones históricas
    """
    try:
        controller = get_explanation_controller()
        result = controller.get_impact_explanation(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando explicación de impacto: {str(e)}")

@explanation_router.get("/asteroid/{neo_id}/trajectory", response_model=TrajectoryExplanationResponse)
async def get_trajectory_explanation(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera explicación de trayectoria orbital
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Explicación de trayectoria con predicciones futuras
    """
    try:
        controller = get_explanation_controller()
        result = controller.get_trajectory_explanation(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando explicación de trayectoria: {str(e)}")

@explanation_router.get("/asteroid/{neo_id}/mitigation", response_model=MitigationExplanationResponse)
async def get_mitigation_explanation(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera explicación de estrategias de mitigación
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Explicación de mitigación con estrategias factibles
    """
    try:
        controller = get_explanation_controller()
        result = controller.get_mitigation_explanation(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando explicación de mitigación: {str(e)}")

@explanation_router.get("/asteroid/{neo_id}/risk", response_model=RiskOverviewResponse)
async def get_risk_overview(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera resumen general de riesgo
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Resumen de riesgo con recomendaciones
    """
    try:
        controller = get_explanation_controller()
        result = controller.get_risk_overview(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando resumen de riesgo: {str(e)}")

# Endpoint de salud específico para explicaciones
@explanation_router.get("/health")
async def explanation_health_check():
    """
    Verifica el estado del servicio de explicaciones
    
    Returns:
        Estado del servicio y estadísticas de explicaciones
    """
    try:
        controller = get_explanation_controller()
        
        return {
            "status": "healthy",
            "service": "Explicaciones Científicas",
            "supported_explanations": [
                "asteroid_basics",
                "impact_analysis",
                "trajectory_analysis", 
                "mitigation_analysis",
                "risk_overview",
                "complete"
            ],
            "features": [
                "Explicaciones en lenguaje natural",
                "Comparaciones históricas",
                "Clasificaciones científicas",
                "Evaluaciones de riesgo",
                "Predicciones futuras"
            ],
            "timestamp": "2024-09-30T18:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Servicio de explicaciones no disponible: {str(e)}")