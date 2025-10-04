"""
Rutas para Predicciones ML
Maneja las peticiones HTTP para generar predicciones de machine learning
"""

from fastapi import APIRouter, HTTPException, Path
from typing import Optional

from ..controllers.ml_prediction_controller import MLPredictionController
from ..models.ml_prediction_models import (
    CompleteMLPredictionResponse,
    TrajectoryPredictionAPIResponse,
    RiskEvolutionAPIResponse,
    ImpactProbabilityAPIResponse,
    HistoricalAnalysisAPIResponse,
    ModelConfidenceAPIResponse
)

# Crear el router para predicciones ML
ml_prediction_router = APIRouter(prefix="/ml-predict", tags=["Predicciones ML"])

# Instancia del controlador (se inicializa solo cuando se necesita)
def get_ml_prediction_controller():
    """Obtiene una instancia del controlador de predicciones ML"""
    return MLPredictionController()

@ml_prediction_router.get("/asteroid/{neo_id}", response_model=CompleteMLPredictionResponse)
async def get_complete_ml_prediction(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera predicciones ML completas del asteroide
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Predicciones ML completas con trayectoria, riesgo, impacto y análisis histórico
    """
    try:
        controller = get_ml_prediction_controller()
        result = controller.get_complete_ml_prediction(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando predicciones ML completas: {str(e)}")

@ml_prediction_router.get("/asteroid/{neo_id}/trajectory", response_model=TrajectoryPredictionAPIResponse)
async def get_trajectory_prediction(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera predicción de trayectoria futura usando ML
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Predicción de trayectoria orbital a 10 años con confianza ML
    """
    try:
        controller = get_ml_prediction_controller()
        result = controller.get_trajectory_prediction(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando predicción de trayectoria: {str(e)}")

@ml_prediction_router.get("/asteroid/{neo_id}/risk-evolution", response_model=RiskEvolutionAPIResponse)
async def get_risk_evolution(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera análisis de evolución de riesgo temporal usando ML
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Evolución de riesgo a 5 años con patrones estacionales ML
    """
    try:
        controller = get_ml_prediction_controller()
        result = controller.get_risk_evolution(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando evolución de riesgo: {str(e)}")

@ml_prediction_router.get("/asteroid/{neo_id}/impact-probability", response_model=ImpactProbabilityAPIResponse)
async def get_impact_probability(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera probabilidades de impacto usando ML
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Probabilidades de impacto para múltiples períodos con clasificación ML
    """
    try:
        controller = get_ml_prediction_controller()
        result = controller.get_impact_probability(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando probabilidad de impacto: {str(e)}")

@ml_prediction_router.get("/asteroid/{neo_id}/historical-analysis", response_model=HistoricalAnalysisAPIResponse)
async def get_historical_analysis(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera análisis de patrones históricos usando ML
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Análisis de asteroides similares con patrones históricos ML
    """
    try:
        controller = get_ml_prediction_controller()
        result = controller.get_historical_analysis(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando análisis histórico: {str(e)}")

@ml_prediction_router.get("/asteroid/{neo_id}/model-confidence", response_model=ModelConfidenceAPIResponse)
async def get_model_confidence(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera análisis de confianza del modelo ML
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Confianza del modelo ML con recomendaciones de mejora
    """
    try:
        controller = get_ml_prediction_controller()
        result = controller.get_model_confidence(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando confianza del modelo: {str(e)}")

# Endpoint de salud específico para predicciones ML
@ml_prediction_router.get("/health")
async def ml_prediction_health_check():
    """
    Verifica el estado del servicio de predicciones ML
    
    Returns:
        Estado del servicio y estadísticas de predicciones ML
    """
    try:
        controller = get_ml_prediction_controller()
        
        return {
            "status": "healthy",
            "service": "Predicciones ML",
            "supported_predictions": [
                "trajectory_prediction",
                "risk_evolution",
                "impact_probability",
                "historical_analysis",
                "model_confidence",
                "complete"
            ],
            "ml_features": [
                "Predicciones de trayectoria a 10 años",
                "Evolución de riesgo temporal con patrones estacionales",
                "Probabilidades de impacto ML para múltiples períodos",
                "Análisis de patrones históricos de asteroides similares",
                "Evaluación de confianza de modelos ML"
            ],
            "model_types": [
                "Orbital Evolution ML",
                "Risk Evolution ML", 
                "Impact Probability ML",
                "Historical Pattern Analysis ML"
            ],
            "timestamp": "2024-09-30T18:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Servicio de predicciones ML no disponible: {str(e)}")