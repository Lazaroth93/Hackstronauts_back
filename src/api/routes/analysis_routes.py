"""
Rutas para Análisis de Asteroides
Maneja las peticiones HTTP para análisis con LangGraph
Siguiendo principios SOLID - Responsabilidad única
"""

from fastapi import APIRouter, HTTPException, Path, Depends
from typing import Optional
from datetime import datetime

from ..controllers.analysis_controller import AnalysisController
from ..models.analysis_models import (
    PhysicalProperties,
    AsteroidAnalysisResponse,
    ConfidenceMetricsResponse,
    ImpactPredictionResponse,
    HybridAnalysisRequest,
    HybridAnalysisResponse
)

# Crear el router para análisis
analysis_router = APIRouter(prefix="/analyze", tags=["Análisis con LangGraph"])

# Instancia del controlador (se inicializa solo cuando se necesita)
def get_analysis_controller():
    """Obtiene una instancia del controlador de análisis"""
    return AnalysisController()


@analysis_router.post("/asteroid", response_model=AsteroidAnalysisResponse)
async def analyze_asteroid(
    physical_properties: PhysicalProperties
):
    """
    Analiza un asteroide usando el sistema LangGraph
    
    - **diameter_m**: Diámetro en metros
    - **velocity_km_s**: Velocidad en km/s
    - **mass_kg**: Masa en kilogramos
    - **density_kg_m3**: Densidad en kg/m³
    
    Returns:
        Análisis completo del asteroide incluyendo:
        - Propiedades físicas calculadas
        - Análisis de impacto
        - Factores de riesgo
        - Evaluación de riesgo
        - Métricas de calidad de datos
    """
    try:
        analysis_controller = get_analysis_controller()
        result = analysis_controller.analyze_asteroid(physical_properties)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el análisis del asteroide: {str(e)}")


@analysis_router.get("/confidence/{neo_id}", response_model=ConfidenceMetricsResponse)
async def get_confidence_metrics(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Obtiene métricas de confianza para las predicciones de un NEO
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Métricas de confianza incluyendo:
        - Calidad de los datos de entrada
        - Confiabilidad de las predicciones
        - Factores que afectan la confianza
        - Recomendaciones para mejorar la precisión
    """
    try:
        analysis_controller = get_analysis_controller()
        result = analysis_controller.get_confidence_metrics(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron métricas de confianza para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener métricas de confianza: {str(e)}")


@analysis_router.post("/predict-impact", response_model=ImpactPredictionResponse)
async def predict_impact(
    physical_properties: PhysicalProperties
):
    """
    Predice el impacto de un asteroide en la Tierra
    
    - **diameter_m**: Diámetro en metros
    - **velocity_km_s**: Velocidad en km/s
    - **mass_kg**: Masa en kilogramos
    - **density_kg_m3**: Densidad en kg/m³
    
    Returns:
        Predicción de impacto incluyendo:
        - Energía cinética y de impacto
        - Diámetro del cráter
        - Radio de daño
        - Área de impacto
        - Probabilidad de impacto
        - Categoría de riesgo
    """
    try:
        analysis_controller = get_analysis_controller()
        result = analysis_controller.predict_impact(physical_properties)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la predicción de impacto: {str(e)}")


@analysis_router.post("/hybrid", response_model=HybridAnalysisResponse)
async def hybrid_analysis(
    analysis_request: HybridAnalysisRequest
):
    """
    Realiza análisis híbrido combinando múltiples fuentes de datos
    
    - **neo_id**: ID del NEO (opcional)
    - **physical_properties**: Propiedades físicas del asteroide
    - **analysis_type**: Tipo de análisis a realizar
    - **include_predictions**: Incluir predicciones de impacto
    - **include_confidence**: Incluir métricas de confianza
    
    Returns:
        Análisis híbrido completo incluyendo:
        - Resumen del análisis
        - Resultados detallados
        - Métricas de confianza
        - Recomendaciones
        - Tiempo de procesamiento
    """
    try:
        analysis_controller = get_analysis_controller()
        result = analysis_controller.hybrid_analysis(analysis_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el análisis híbrido: {str(e)}")


# Endpoint de salud específico para análisis
@analysis_router.get("/health")
async def analysis_health_check():
    """
    Verifica el estado del servicio de análisis
    
    Returns:
        Estado del servicio y estadísticas de análisis
    """
    try:
        # Obtener estadísticas básicas del servicio
        analysis_controller = get_analysis_controller()
        stats = analysis_controller.get_service_stats()
        
        return {
            "status": "healthy",
            "service": "Análisis con LangGraph",
            "total_analyses": stats.get("total_analyses", 0),
            "avg_processing_time": stats.get("avg_processing_time", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Servicio de análisis no disponible: {str(e)}")