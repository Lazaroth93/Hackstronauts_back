"""
Modelos Pydantic para explicaciones científicas
Define las estructuras de datos para las respuestas de explicación
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class AsteroidBasicExplanation(BaseModel):
    """Explicación básica del asteroide"""
    summary: str
    key_facts: List[str]
    scientific_context: str
    size_category: str
    hazard_level: str

class ImpactExplanation(BaseModel):
    """Explicación de efectos de impacto"""
    summary: str
    energy_comparison: str
    damage_assessment: Dict[str, str]
    historical_comparison: str
    impact_zones: Dict[str, float]
    severity_level: str

class TrajectoryExplanation(BaseModel):
    """Explicación de trayectoria orbital"""
    summary: str
    orbital_characteristics: Dict[str, str]
    future_predictions: Dict[str, str]
    approach_analysis: Dict[str, Any]
    orbital_data: Dict[str, float]
    risk_assessment: str

class MitigationExplanation(BaseModel):
    """Explicación de estrategias de mitigación"""
    summary: str
    feasible_strategies: List[str]
    cost_benefit: str
    implementation_timeline: str
    success_probability: str

class RiskOverviewExplanation(BaseModel):
    """Resumen general de riesgo"""
    overall_risk: str
    key_concerns: List[str]
    recommendations: List[str]
    monitoring_priority: str

class CompleteExplanationResponse(BaseModel):
    """Respuesta completa de explicación"""
    neo_id: str
    neo_name: str
    explanation_type: str = "complete"
    asteroid_basics: Optional[AsteroidBasicExplanation] = None
    impact_analysis: Optional[ImpactExplanation] = None
    trajectory_analysis: Optional[TrajectoryExplanation] = None
    mitigation_analysis: Optional[MitigationExplanation] = None
    risk_overview: Optional[RiskOverviewExplanation] = None
    generated_at: datetime
    confidence_score: Optional[float] = None

class AsteroidBasicResponse(BaseModel):
    """Respuesta de explicación básica del asteroide"""
    neo_id: str
    neo_name: str
    explanation_type: str = "asteroid_basics"
    data: AsteroidBasicExplanation
    generated_at: datetime

class ImpactExplanationResponse(BaseModel):
    """Respuesta de explicación de impacto"""
    neo_id: str
    neo_name: str
    explanation_type: str = "impact"
    data: ImpactExplanation
    generated_at: datetime

class TrajectoryExplanationResponse(BaseModel):
    """Respuesta de explicación de trayectoria"""
    neo_id: str
    neo_name: str
    explanation_type: str = "trajectory"
    data: TrajectoryExplanation
    generated_at: datetime

class MitigationExplanationResponse(BaseModel):
    """Respuesta de explicación de mitigación"""
    neo_id: str
    neo_name: str
    explanation_type: str = "mitigation"
    data: MitigationExplanation
    generated_at: datetime

class RiskOverviewResponse(BaseModel):
    """Respuesta de resumen de riesgo"""
    neo_id: str
    neo_name: str
    explanation_type: str = "risk_overview"
    data: RiskOverviewExplanation
    generated_at: datetime
