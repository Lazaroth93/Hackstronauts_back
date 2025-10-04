"""
Modelos Pydantic para Métricas del Sistema
Siguiendo principios SOLID - Responsabilidad única por modelo
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List
from datetime import datetime


class SizeMetrics(BaseModel):
    """Métricas de tamaño de NEOs"""
    total_count: int = Field(..., description="Número total de NEOs")
    avg_min_diameter: float = Field(..., description="Diámetro mínimo promedio")
    avg_max_diameter: float = Field(..., description="Diámetro máximo promedio")
    avg_diameter: float = Field(..., description="Diámetro promedio")
    min_diameter: float = Field(..., description="Diámetro mínimo")
    max_diameter: float = Field(..., description="Diámetro máximo")
    diameter_stddev: float = Field(..., description="Desviación estándar del diámetro")


class VelocityMetrics(BaseModel):
    """Métricas de velocidad de NEOs"""
    total_count: int = Field(..., description="Número total de NEOs")
    avg_velocity: float = Field(..., description="Velocidad promedio")
    min_velocity: float = Field(..., description="Velocidad mínima")
    max_velocity: float = Field(..., description="Velocidad máxima")
    velocity_stddev: float = Field(..., description="Desviación estándar de la velocidad")
    median_velocity: float = Field(..., description="Velocidad mediana")


class MagnitudeMetrics(BaseModel):
    """Métricas de magnitud de NEOs"""
    total_count: int = Field(..., description="Número total de NEOs")
    avg_magnitude: float = Field(..., description="Magnitud promedio")
    min_magnitude: float = Field(..., description="Magnitud mínima")
    max_magnitude: float = Field(..., description="Magnitud máxima")
    magnitude_stddev: float = Field(..., description="Desviación estándar de la magnitud")


class SizeMetricsResponse(BaseModel):
    """Respuesta de métricas de tamaño"""
    size_metrics: SizeMetrics = Field(..., description="Métricas de tamaño")
    timestamp: datetime = Field(..., description="Timestamp de la consulta")


class VelocityMetricsResponse(BaseModel):
    """Respuesta de métricas de velocidad"""
    velocity_metrics: VelocityMetrics = Field(..., description="Métricas de velocidad")
    timestamp: datetime = Field(..., description="Timestamp de la consulta")


class MagnitudeMetricsResponse(BaseModel):
    """Respuesta de métricas de magnitud"""
    magnitude_metrics: MagnitudeMetrics = Field(..., description="Métricas de magnitud")
    timestamp: datetime = Field(..., description="Timestamp de la consulta")


class AgentStatus(BaseModel):
    """Estado de un agente"""
    rag_agent: str = Field(..., description="Estado del agente RAG")
    prediction_agent: str = Field(..., description="Estado del agente de predicción")
    dashboard_agent: str = Field(..., description="Estado del agente de dashboard")
    ingestor: str = Field(..., description="Estado del ingestor")


class SystemStatistics(BaseModel):
    """Estadísticas del sistema"""
    total_neos: int = Field(..., description="Total de NEOs")
    hazardous_neos: int = Field(..., description="NEOs peligrosos")
    total_predictions: int = Field(..., description="Total de predicciones")
    total_documents: int = Field(..., description="Total de documentos")
    average_risk_score: float = Field(..., description="Puntuación promedio de riesgo")


class SystemStatusResponse(BaseModel):
    """Respuesta de estado del sistema"""
    timestamp: datetime = Field(..., description="Timestamp del estado")
    database_status: str = Field(..., description="Estado de la base de datos")
    agent_status: AgentStatus = Field(..., description="Estado de los agentes")
    statistics: SystemStatistics = Field(..., description="Estadísticas del sistema")
    system_health: str = Field(..., description="Salud general del sistema")


class DashboardMetric(BaseModel):
    """Métrica del dashboard"""
    id: int = Field(..., description="ID de la métrica")
    metric_name: str = Field(..., description="Nombre de la métrica")
    value: float = Field(..., description="Valor de la métrica")
    created_at: datetime = Field(..., description="Fecha de creación")


class MetricsResponse(BaseModel):
    """Respuesta de métricas del dashboard"""
    metrics: List[DashboardMetric] = Field(..., description="Lista de métricas")


class PredictionMetric(BaseModel):
    """Métrica de predicción"""
    id: int = Field(..., description="ID de la predicción")
    neo_id: str = Field(..., description="ID del NEO")
    predicted_close_approach_date: str = Field(..., description="Fecha de aproximación predicha")
    predicted_miss_distance_km: float = Field(..., description="Distancia de paso predicha")
    risk_score: float = Field(..., description="Puntuación de riesgo")
    created_at: datetime = Field(..., description="Fecha de creación")


class PredictionsResponse(BaseModel):
    """Respuesta de predicciones"""
    predictions: List[PredictionMetric] = Field(..., description="Lista de predicciones")


class VectorSearchResult(BaseModel):
    """Resultado de búsqueda vectorial"""
    id: int = Field(..., description="ID del documento")
    source: str = Field(..., description="Fuente del documento")
    content: str = Field(..., description="Contenido del documento")
    metadata: Dict[str, Any] = Field(..., description="Metadatos del documento")
    distance: float = Field(..., description="Distancia de similitud")


class VectorSearchResponse(BaseModel):
    """Respuesta de búsqueda vectorial"""
    results: List[VectorSearchResult] = Field(..., description="Resultados de la búsqueda")


# Modelos para predicciones ML
class TrajectoryPredictionResponse(BaseModel):
    """Respuesta de predicción de trayectoria"""
    neo_id: str = Field(..., description="ID del NEO")
    prediction_date: datetime = Field(..., description="Fecha de la predicción")
    future_positions: List[Dict[str, Any]] = Field(..., description="Posiciones futuras predichas")
    confidence_score: float = Field(..., description="Puntuación de confianza")
    prediction_horizon_days: int = Field(..., description="Horizonte de predicción en días")


class RiskEvolutionResponse(BaseModel):
    """Respuesta de evolución de riesgo"""
    neo_id: str = Field(..., description="ID del NEO")
    analysis_date: datetime = Field(..., description="Fecha del análisis")
    risk_timeline: List[Dict[str, Any]] = Field(..., description="Línea de tiempo del riesgo")
    peak_risk_date: str = Field(..., description="Fecha de mayor riesgo")
    peak_risk_score: float = Field(..., description="Puntuación máxima de riesgo")


class ImpactProbabilityResponse(BaseModel):
    """Respuesta de probabilidad de impacto"""
    neo_id: str = Field(..., description="ID del NEO")
    prediction_date: datetime = Field(..., description="Fecha de la predicción")
    impact_probability: float = Field(..., description="Probabilidad de impacto")
    impact_date_range: Dict[str, str] = Field(..., description="Rango de fechas de impacto")
    confidence_interval: Dict[str, float] = Field(..., description="Intervalo de confianza")


class HistoricalAnalysisResponse(BaseModel):
    """Respuesta de análisis histórico"""
    neo_id: str = Field(..., description="ID del NEO")
    analysis_date: datetime = Field(..., description="Fecha del análisis")
    historical_approaches: List[Dict[str, Any]] = Field(..., description="Aproximaciones históricas")
    risk_trend: str = Field(..., description="Tendencia del riesgo")
    pattern_analysis: str = Field(..., description="Análisis de patrones")


class ModelConfidenceResponse(BaseModel):
    """Respuesta de confianza del modelo"""
    neo_id: str = Field(..., description="ID del NEO")
    analysis_date: datetime = Field(..., description="Fecha del análisis")
    model_accuracy: float = Field(..., description="Precisión del modelo")
    prediction_confidence: float = Field(..., description="Confianza de la predicción")
    data_quality_score: float = Field(..., description="Puntuación de calidad de datos")


class CompleteMLPredictionResponse(BaseModel):
    """Respuesta completa de predicción ML"""
    neo_id: str = Field(..., description="ID del NEO")
    prediction_date: datetime = Field(..., description="Fecha de la predicción")
    trajectory_prediction: TrajectoryPredictionResponse = Field(..., description="Predicción de trayectoria")
    risk_evolution: RiskEvolutionResponse = Field(..., description="Evolución del riesgo")
    impact_probability: ImpactProbabilityResponse = Field(..., description="Probabilidad de impacto")
    historical_analysis: HistoricalAnalysisResponse = Field(..., description="Análisis histórico")
    model_confidence: ModelConfidenceResponse = Field(..., description="Confianza del modelo")


# Modelos de respuesta API
class TrajectoryPredictionAPIResponse(BaseModel):
    """Respuesta API de predicción de trayectoria"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje de respuesta")
    data: TrajectoryPredictionResponse = Field(..., description="Datos de la predicción")


class RiskEvolutionAPIResponse(BaseModel):
    """Respuesta API de evolución de riesgo"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje de respuesta")
    data: RiskEvolutionResponse = Field(..., description="Datos de evolución de riesgo")


class ImpactProbabilityAPIResponse(BaseModel):
    """Respuesta API de probabilidad de impacto"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje de respuesta")
    data: ImpactProbabilityResponse = Field(..., description="Datos de probabilidad de impacto")


class HistoricalAnalysisAPIResponse(BaseModel):
    """Respuesta API de análisis histórico"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje de respuesta")
    data: HistoricalAnalysisResponse = Field(..., description="Datos de análisis histórico")


class ModelConfidenceAPIResponse(BaseModel):
    """Respuesta API de confianza del modelo"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje de respuesta")
    data: ModelConfidenceResponse = Field(..., description="Datos de confianza del modelo")
