"""
Modelos Pydantic para NEOs (Near Earth Objects)
Siguiendo principios SOLID - Responsabilidad única por modelo
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum


class RiskCategory(str, Enum):
    """Categorías de riesgo para NEOs"""
    VERY_LOW = "Muy Bajo"
    LOW = "Bajo"
    MODERATE = "Moderado"
    HIGH = "Alto"
    CRITICAL = "Crítico"


class NEOSearchQuery(BaseModel):
    """Modelo para búsqueda de NEOs"""
    query: str = Field(..., description="Término de búsqueda")
    limit: int = Field(20, ge=1, le=100, description="Número máximo de resultados")
    hazardous_only: bool = Field(False, description="Filtrar solo NEOs peligrosos")
    min_diameter: Optional[float] = Field(None, ge=0, description="Diámetro mínimo en metros")
    max_diameter: Optional[float] = Field(None, ge=0, description="Diámetro máximo en metros")
    min_velocity: Optional[float] = Field(None, ge=0, description="Velocidad mínima en km/s")
    max_velocity: Optional[float] = Field(None, ge=0, description="Velocidad máxima en km/s")


class ImpactPredictionRequest(BaseModel):
    """Modelo para solicitud de predicción de impacto"""
    neo_id: str = Field(..., description="ID del NEO")
    approach_date: Optional[date] = Field(None, description="Fecha de aproximación")
    custom_velocity: Optional[float] = Field(None, ge=0, description="Velocidad personalizada en km/s")
    custom_diameter: Optional[float] = Field(None, ge=0, description="Diámetro personalizado en metros")


class HybridAnalysisRequest(BaseModel):
    """Modelo para análisis híbrido de múltiples NEOs"""
    neo_ids: List[str] = Field(..., min_items=1, description="Lista de IDs de NEOs")
    analysis_type: str = Field("comprehensive", description="Tipo de análisis")


class EmbeddingQuery(BaseModel):
    """Modelo para consultas de búsqueda vectorial"""
    embedding: List[float] = Field(..., description="Vector de embedding")
    top_k: int = Field(5, ge=1, le=50, description="Número de resultados top")
    source: Optional[str] = Field(None, description="Filtro por fuente")


class NEOResponse(BaseModel):
    """Modelo de respuesta para un NEO individual"""
    neo_id: str
    name: str
    close_approach_date: Optional[date]
    miss_distance_km: Optional[float]
    diameter_min_m: Optional[float]
    diameter_max_m: Optional[float]
    velocity_km_s: Optional[float]
    is_potentially_hazardous: bool
    risk_score: Optional[float]
    risk_category: Optional[RiskCategory]
    impact_energy_mt: Optional[float]
    crater_diameter_km: Optional[float]
    damage_radius_km: Optional[float]


class NEOSListResponse(BaseModel):
    """Modelo de respuesta para lista de NEOs con paginación"""
    neos: List[NEOResponse]
    pagination: Dict[str, Any]


class DangerousNEOResponse(BaseModel):
    """Modelo de respuesta para NEOs peligrosos"""
    dangerous_neos: List[NEOResponse]
    count: int


class SearchResponse(BaseModel):
    """Modelo de respuesta para búsqueda de NEOs"""
    results: List[NEOResponse]
    count: int
    query: Dict[str, Any]


class ApproachResponse(BaseModel):
    """Modelo de respuesta para aproximaciones de un NEO"""
    neo_id: str
    approaches: List[Dict[str, Any]]
    total_approaches: int


class UpcomingApproachesResponse(BaseModel):
    """Modelo de respuesta para próximas aproximaciones"""
    upcoming_approaches: List[NEOResponse]
    count: int
    days_ahead: int
