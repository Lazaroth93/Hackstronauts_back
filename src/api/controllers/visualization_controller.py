"""
Controlador para Visualizaciones
Contiene la lógica de negocio para generar gráficos y visualizaciones
"""

import os
import psycopg2
import psycopg2.extras
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import math

from ..models.visualization_models import (
    OrbitalTrajectoryResponse,
    ImpactMapResponse,
    ConfidenceChartResponse,
    RiskTimelineResponse,
    Orbit3DResponse,
    OrbitalTrajectoryData,
    ImpactMapData,
    ConfidenceChartData,
    RiskTimelineData,
    Orbit3DData,
    ImpactZone,
    RiskEvent,
    Orbit3DPoint,
    ChartConfig
)


class VisualizationController:
    """
    Controlador para operaciones de visualización
    
    Responsabilidades:
    - Generar gráficos de trayectorias orbitales
    - Crear mapas de impacto con zonas de daño
    - Producir gráficos de métricas de confianza
    - Generar timelines de riesgo temporal
    - Crear visualizaciones 3D de órbitas
    """
    
    def __init__(self):
        """Inicializa la conexión a la base de datos"""
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL no está configurada")
    
    def _get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return psycopg2.connect(
            self.database_url, 
            cursor_factory=psycopg2.extras.RealDictCursor
        )
    
    def get_orbital_trajectory(self, neo_id: str) -> Optional[OrbitalTrajectoryResponse]:
        """
        Genera gráfico de trayectoria orbital
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Datos de trayectoria orbital o None si no se encuentra
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Obtener datos del NEO
            cursor.execute("""
                SELECT n.*, np.risk_score, np.confidence_score
                FROM neos n
                LEFT JOIN neo_predictions np ON n.neo_id = np.neo_id
                WHERE n.neo_id = %s
            """, (neo_id,))
            
            neo_data = cursor.fetchone()
            if not neo_data:
                return None
            
            # Obtener aproximaciones cercanas
            cursor.execute("""
                SELECT close_approach_date, miss_distance_km, relative_velocity_km_s
                FROM neos_close_approaches
                WHERE neo_id = %s
                ORDER BY close_approach_date
                LIMIT 10
            """, (neo_id,))
            
            approaches = cursor.fetchall()
            
            # Generar datos de trayectoria (simplificado)
            time_points = []
            distance_points = []
            velocity_points = []
            
            for i, approach in enumerate(approaches):
                time_points.append(i * 30)  # Días
                distance_points.append(float(approach['miss_distance_km']) / 1.496e8)  # Convertir a UA
                velocity_points.append(approach['relative_velocity_km_s'])
            
            # Encontrar aproximación más cercana
            closest_approach = None
            if approaches:
                closest = min(approaches, key=lambda x: x['miss_distance_km'])
                closest_approach = {
                    "date": closest['close_approach_date'].isoformat(),
                    "distance_km": closest['miss_distance_km'],
                    "velocity_km_s": closest['relative_velocity_km_s']
                }
            
            cursor.close()
            conn.close()
            
            return OrbitalTrajectoryResponse(
                neo_id=neo_id,
                neo_name=neo_data['name'],
                title=f"Trayectoria Orbital - {neo_data['name']}",
                data=OrbitalTrajectoryData(
                    time_points=time_points,
                    distance_points=distance_points,
                    velocity_points=velocity_points,
                    closest_approach=closest_approach
                ),
                config=ChartConfig(
                    color="#2E86AB",
                    width=800,
                    height=600,
                    chart_type="line"
                ),
                generated_at=datetime.utcnow(),
                confidence_score=neo_data.get('confidence_score', 0.5)
            )
            
        except Exception as e:
            print(f"Error generando trayectoria orbital: {e}")
            return None
    
    def get_impact_map(self, neo_id: str) -> Optional[ImpactMapResponse]:
        """
        Genera mapa de impacto con zonas de daño
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Datos de mapa de impacto o None si no se encuentra
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Obtener datos del NEO y predicciones
            cursor.execute("""
                SELECT n.*, np.impact_energy_mt, np.crater_diameter_km, 
                       np.seismic_radius_km, np.tsunami_radius_km, np.thermal_radius_km, np.blast_radius_km
                FROM neos n
                LEFT JOIN neo_predictions np ON n.neo_id = np.neo_id
                WHERE n.neo_id = %s
            """, (neo_id,))
            
            neo_data = cursor.fetchone()
            if not neo_data:
                return None
            
            # Generar zonas de impacto (simplificado)
            zones = []
            center_lat = 0.0  # Coordenadas de ejemplo
            center_lon = 0.0
            
            if neo_data.get('crater_diameter_km'):
                zones.append(ImpactZone(
                    zone_type="crater",
                    center_lat=center_lat,
                    center_lon=center_lon,
                    radius_km=neo_data['crater_diameter_km'] / 2,
                    severity="extreme"
                ))
            
            if neo_data.get('seismic_radius_km'):
                zones.append(ImpactZone(
                    zone_type="seismic",
                    center_lat=center_lat,
                    center_lon=center_lon,
                    radius_km=neo_data['seismic_radius_km'],
                    severity="high"
                ))
            
            if neo_data.get('tsunami_radius_km'):
                zones.append(ImpactZone(
                    zone_type="tsunami",
                    center_lat=center_lat,
                    center_lon=center_lon,
                    radius_km=neo_data['tsunami_radius_km'],
                    severity="high"
                ))
            
            cursor.close()
            conn.close()
            
            return ImpactMapResponse(
                neo_id=neo_id,
                neo_name=neo_data['name'],
                title=f"Mapa de Impacto - {neo_data['name']}",
                data=ImpactMapData(
                    center_lat=center_lat,
                    center_lon=center_lon,
                    zones=zones,
                    total_energy_mt=neo_data.get('impact_energy_mt', 0),
                    crater_diameter_km=neo_data.get('crater_diameter_km', 0)
                ),
                config={
                    "map_type": "satellite",
                    "zoom_level": 6
                },
                generated_at=datetime.utcnow(),
                confidence_score=neo_data.get('confidence_score', 0.5)
            )
            
        except Exception as e:
            print(f"Error generando mapa de impacto: {e}")
            return None
    
    def get_confidence_chart(self, neo_id: str) -> Optional[ConfidenceChartResponse]:
        """
        Genera gráfico de métricas de confianza
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Datos de gráfico de confianza o None si no se encuentra
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Obtener métricas de confianza
            cursor.execute("""
                SELECT np.analysis_confidence, np.data_quality_score, 
                       np.orbital_uncertainty, np.prediction_accuracy, np.confidence_score
                FROM neo_predictions np
                WHERE np.neo_id = %s
            """, (neo_id,))
            
            confidence_data = cursor.fetchone()
            if not confidence_data:
                return None
            
            # Obtener nombre del NEO
            cursor.execute("SELECT name FROM neos WHERE neo_id = %s", (neo_id,))
            neo_name = cursor.fetchone()['name']
            
            cursor.close()
            conn.close()
            
            # Preparar datos para el gráfico
            categories = ["Análisis", "Calidad", "Orbital", "Predicción", "General"]
            values = [
                confidence_data.get('analysis_confidence', 0.5),
                confidence_data.get('data_quality_score', 0.5),
                1.0 - float(confidence_data.get('orbital_uncertainty', 0.5)),  # Invertir incertidumbre
                confidence_data.get('prediction_accuracy', 0.5),
                confidence_data.get('confidence_score', 0.5)
            ]
            colors = ["#F6AE2D", "#06D6A0", "#2E86AB", "#7209B7", "#F24236"]
            
            return ConfidenceChartResponse(
                neo_id=neo_id,
                neo_name=neo_name,
                title="Métricas de Confianza del Sistema",
                data=ConfidenceChartData(
                    categories=categories,
                    values=values,
                    colors=colors,
                    overall_confidence=confidence_data.get('confidence_score', 0.5)
                ),
                config=ChartConfig(
                    color="#F6AE2D",
                    width=600,
                    height=600,
                    chart_type="radar"
                ),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando gráfico de confianza: {e}")
            return None
    
    def get_risk_timeline(self, neo_id: str) -> Optional[RiskTimelineResponse]:
        """
        Genera timeline de riesgo temporal
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Datos de timeline de riesgo o None si no se encuentra
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Obtener aproximaciones cercanas futuras
            cursor.execute("""
                SELECT close_approach_date, miss_distance_km, relative_velocity_km_s
                FROM neos_close_approaches
                WHERE neo_id = %s AND close_approach_date >= CURRENT_DATE
                ORDER BY close_approach_date
                LIMIT 5
            """, (neo_id,))
            
            approaches = cursor.fetchall()
            
            # Obtener nombre del NEO
            cursor.execute("SELECT name FROM neos WHERE neo_id = %s", (neo_id,))
            neo_name = cursor.fetchone()['name']
            
            cursor.close()
            conn.close()
            
            # Generar eventos de riesgo
            events = []
            for approach in approaches:
                distance_km = approach['miss_distance_km']
                if distance_km < 1000000:  # Menos de 1M km
                    risk_level = "high"
                elif distance_km < 5000000:  # Menos de 5M km
                    risk_level = "medium"
                else:
                    risk_level = "low"
                
                events.append(RiskEvent(
                    date=approach['close_approach_date'].isoformat(),
                    risk_level=risk_level,
                    description=f"Aproximación a {distance_km/1000:.0f}K km",
                    probability=0.1 if risk_level == "high" else 0.01
                ))
            
            return RiskTimelineResponse(
                neo_id=neo_id,
                neo_name=neo_name,
                title="Timeline de Riesgo",
                data=RiskTimelineData(
                    events=events,
                    risk_levels=[
                        {"level": "low", "color": "#06D6A0"},
                        {"level": "medium", "color": "#F6AE2D"},
                        {"level": "high", "color": "#F24236"}
                    ],
                    time_range_days=365
                ),
                config={
                    "time_range": "365_days",
                    "risk_threshold": 0.5
                },
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando timeline de riesgo: {e}")
            return None
    
    def get_orbit_3d(self, neo_id: str) -> Optional[Orbit3DResponse]:
        """
        Genera visualización 3D de órbita
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Datos de órbita 3D o None si no se encuentra
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Obtener datos orbitales (simplificado)
            cursor.execute("""
                SELECT n.name, nca.close_approach_date, nca.miss_distance_km
                FROM neos n
                LEFT JOIN neos_close_approaches nca ON n.neo_id = nca.neo_id
                WHERE n.neo_id = %s
                ORDER BY nca.close_approach_date
                LIMIT 20
            """, (neo_id,))
            
            approaches = cursor.fetchall()
            if not approaches:
                return None
            
            neo_name = approaches[0]['name']
            
            # Generar puntos de órbita (simplificado)
            orbit_points = []
            for i, approach in enumerate(approaches):
                angle = (i / len(approaches)) * 2 * math.pi
                radius = float(approach['miss_distance_km']) / 1.496e8  # Convertir a UA
                
                orbit_points.append(Orbit3DPoint(
                    x=radius * math.cos(angle),
                    y=radius * math.sin(angle),
                    z=0.1 * math.sin(angle * 2),  # Pequeña variación en Z
                    time=i * 30  # Días
                ))
            
            cursor.close()
            conn.close()
            
            return Orbit3DResponse(
                neo_id=neo_id,
                neo_name=neo_name,
                title=f"Órbita 3D - {neo_name}",
                data=Orbit3DData(
                    orbit_points=orbit_points,
                    earth_position=[0, 0, 0],
                    asteroid_position=[orbit_points[0].x, orbit_points[0].y, orbit_points[0].z] if orbit_points else [0, 0, 0],
                    camera_position=[10, 10, 10]
                ),
                config={
                    "animation_speed": 1.0,
                    "show_earth": True,
                    "show_trajectory": True
                },
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando visualización 3D: {e}")
            return None
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del servicio de visualizaciones"""
        return {
            "total_visualizations": 0,  # Se implementaría con contadores reales
            "supported_types": 5,
            "last_generated": datetime.utcnow().isoformat()
        }