
"""
Modelos Pydantic para visualizaciones
Define las estructuras de datos para las respuestas de visualización
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChartData(BaseModel):
    """Datos base para gráficos"""
    x_axis: str
    y_axis: str
    points: List[Dict[str, Any]]
    labels: Optional[List[str]] = None

class ChartConfig(BaseModel):
    """Configuración de gráficos"""
    color: str
    width: int = 800
    height: int = 600
    chart_type: Optional[str] = None

class OrbitalTrajectoryData(BaseModel):
    """Datos de trayectoria orbital"""
    time_points: List[float]  # Días desde ahora
    distance_points: List[float]  # Distancia en UA
    velocity_points: List[float]  # Velocidad en km/s
    closest_approach: Optional[Dict[str, Any]] = None

class OrbitalTrajectoryResponse(BaseModel):
    """Respuesta de trayectoria orbital"""
    neo_id: str
    neo_name: str
    chart_type: str = "orbital_trajectory"
    title: str
    data: OrbitalTrajectoryData
    config: ChartConfig
    generated_at: datetime
    confidence_score: Optional[float] = None

class ImpactZone(BaseModel):
    """Zona de impacto"""
    zone_type: str  # "crater", "seismic", "tsunami", "thermal", "blast"
    center_lat: float
    center_lon: float
    radius_km: float
    severity: str  # "low", "medium", "high", "extreme"

class ImpactMapData(BaseModel):
    """Datos de mapa de impacto"""
    center_lat: float
    center_lon: float
    zones: List[ImpactZone]
    total_energy_mt: float
    crater_diameter_km: float

class ImpactMapResponse(BaseModel):
    """Respuesta de mapa de impacto"""
    neo_id: str
    neo_name: str
    chart_type: str = "impact_map"
    title: str
    data: ImpactMapData
    config: Dict[str, Any]
    generated_at: datetime
    confidence_score: Optional[float] = None

class ConfidenceMetric(BaseModel):
    """Métrica de confianza individual"""
    name: str
    value: float
    max_value: float = 1.0
    color: str

class ConfidenceChartData(BaseModel):
    """Datos de gráfico de confianza"""
    categories: List[str]
    values: List[float]
    colors: List[str]
    overall_confidence: float

class ConfidenceChartResponse(BaseModel):
    """Respuesta de gráfico de confianza"""
    neo_id: str
    neo_name: str
    chart_type: str = "confidence_chart"
    title: str
    data: ConfidenceChartData
    config: ChartConfig
    generated_at: datetime

class RiskEvent(BaseModel):
    """Evento de riesgo temporal"""
    date: str
    risk_level: str  # "low", "medium", "high", "extreme"
    description: str
    probability: float

class RiskTimelineData(BaseModel):
    """Datos de timeline de riesgo"""
    events: List[RiskEvent]
    risk_levels: List[Dict[str, Any]]
    time_range_days: int

class RiskTimelineResponse(BaseModel):
    """Respuesta de timeline de riesgo"""
    neo_id: str
    neo_name: str
    chart_type: str = "risk_timeline"
    title: str
    data: RiskTimelineData
    config: Dict[str, Any]
    generated_at: datetime

class Orbit3DPoint(BaseModel):
    """Punto 3D de órbita"""
    x: float
    y: float
    z: float
    time: float

class Orbit3DData(BaseModel):
    """Datos de órbita 3D"""
    orbit_points: List[Orbit3DPoint]
    earth_position: List[float]
    asteroid_position: List[float]
    camera_position: List[float]

class Orbit3DResponse(BaseModel):
    """Respuesta de órbita 3D"""
    neo_id: str
    neo_name: str
    chart_type: str = "orbit_3d"
    title: str
    data: Orbit3DData
    config: Dict[str, Any]
    generated_at: datetime