"""
Modelos Pydantic para Análisis de Asteroides
Siguiendo principios SOLID - Responsabilidad única por modelo
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class PhysicalProperties(BaseModel):
    """Propiedades físicas de un asteroide"""
    diameter_m: float = Field(..., description="Diámetro en metros")
    velocity_km_s: float = Field(..., description="Velocidad en km/s")
    mass_kg: float = Field(..., description="Masa en kilogramos")
    density_kg_m3: float = Field(..., description="Densidad en kg/m³")


class ImpactAnalysis(BaseModel):
    """Análisis de impacto de un asteroide"""
    kinetic_energy_j: float = Field(..., description="Energía cinética en Joules")
    impact_energy_mt: float = Field(..., description="Energía de impacto en megatones")
    crater_diameter_km: float = Field(..., description="Diámetro del cráter en km")
    damage_radius_km: float = Field(..., description="Radio de daño en km")


class RiskFactors(BaseModel):
    """Factores de riesgo individuales"""
    size_risk: float = Field(..., description="Riesgo por tamaño")
    velocity_risk: float = Field(..., description="Riesgo por velocidad")
    proximity_risk: float = Field(..., description="Riesgo por proximidad")
    energy_risk: float = Field(..., description="Riesgo por energía")


class RiskAssessment(BaseModel):
    """Evaluación de riesgo completa"""
    total_risk_score: float = Field(..., description="Puntuación total de riesgo")
    risk_factors: RiskFactors = Field(..., description="Factores de riesgo")
    risk_category: str = Field(..., description="Categoría de riesgo")


class AsteroidAnalysisResponse(BaseModel):
    """Respuesta completa de análisis de asteroide"""
    neo_id: str = Field(..., description="ID del NEO")
    analysis_date: datetime = Field(..., description="Fecha del análisis")
    physical_properties: PhysicalProperties = Field(..., description="Propiedades físicas")
    impact_analysis: ImpactAnalysis = Field(..., description="Análisis de impacto")
    risk_assessment: RiskAssessment = Field(..., description="Evaluación de riesgo")
    confidence_level: float = Field(..., description="Nivel de confianza")


class DataQuality(BaseModel):
    """Calidad de los datos"""
    completeness: float = Field(..., description="Completitud de los datos")
    consistency: float = Field(..., description="Consistencia de los datos")
    recency: float = Field(..., description="Actualidad de los datos")


class PredictionReliability(BaseModel):
    """Confiabilidad de las predicciones"""
    prediction_count: int = Field(..., description="Número de predicciones")
    avg_risk_score: float = Field(..., description="Puntuación promedio de riesgo")
    risk_score_stddev: float = Field(..., description="Desviación estándar del riesgo")
    confidence_level: float = Field(..., description="Nivel de confianza")


class ConfidenceMetricsResponse(BaseModel):
    """Respuesta de métricas de confianza"""
    neo_id: str = Field(..., description="ID del NEO")
    data_quality: DataQuality = Field(..., description="Calidad de los datos")
    prediction_reliability: PredictionReliability = Field(..., description="Confiabilidad de predicciones")
    overall_confidence: float = Field(..., description="Confianza general")


class ImpactPredictionResponse(BaseModel):
    """Respuesta de predicción de impacto"""
    neo_id: str = Field(..., description="ID del NEO")
    prediction_date: datetime = Field(..., description="Fecha de la predicción")
    approach_date: str = Field(..., description="Fecha de aproximación")
    impact_probability: float = Field(..., description="Probabilidad de impacto")
    impact_energy_mt: float = Field(..., description="Energía de impacto en megatones")
    crater_diameter_km: float = Field(..., description="Diámetro del cráter en km")
    damage_radius_km: float = Field(..., description="Radio de daño en km")
    impact_area_km2: float = Field(..., description="Área de impacto en km²")
    tsunami_potential: bool = Field(..., description="Potencial de tsunami")
    airburst_altitude_km: float = Field(..., description="Altitud de explosión en km")
    fireball_duration_seconds: float = Field(..., description="Duración de la bola de fuego en segundos")


class HybridAnalysisRequest(BaseModel):
    """Solicitud de análisis híbrido"""
    neo_id: Optional[str] = Field(None, description="ID del NEO (opcional)")
    physical_properties: Optional[PhysicalProperties] = Field(None, description="Propiedades físicas del asteroide")
    analysis_type: str = Field("comprehensive", description="Tipo de análisis a realizar")
    include_predictions: bool = Field(True, description="Incluir predicciones de impacto")
    include_confidence: bool = Field(True, description="Incluir métricas de confianza")


class HybridAnalysisSummary(BaseModel):
    """Resumen del análisis híbrido"""
    total_risk_score: float = Field(..., description="Puntuación total de riesgo")
    average_risk_score: float = Field(..., description="Puntuación promedio de riesgo")
    high_risk_count: int = Field(..., description="Número de NEOs de alto riesgo")
    hazardous_count: int = Field(..., description="Número de NEOs peligrosos")
    total_impact_energy: float = Field(..., description="Energía total de impacto")


class HybridAnalysisResponse(BaseModel):
    """Respuesta completa de análisis híbrido"""
    analysis_type: str = Field(..., description="Tipo de análisis")
    analysis_date: datetime = Field(..., description="Fecha del análisis")
    neos_analyzed: int = Field(..., description="Número de NEOs analizados")
    summary: HybridAnalysisSummary = Field(..., description="Resumen del análisis")
    detailed_analysis: List[Dict[str, Any]] = Field(..., description="Análisis detallado")
    recommendations: List[str] = Field(..., description="Recomendaciones")
