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
