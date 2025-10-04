"""
Controlador para Explicaciones Científicas
Contiene la lógica de negocio para generar explicaciones comprensibles
"""

import os
import psycopg2
import psycopg2.extras
from typing import Dict, Any, Optional
from datetime import datetime

from ..models.explanation_models import (
    CompleteExplanationResponse,
    AsteroidBasicResponse,
    ImpactExplanationResponse,
    TrajectoryExplanationResponse,
    MitigationExplanationResponse,
    RiskOverviewResponse,
    AsteroidBasicExplanation,
    ImpactExplanation,
    TrajectoryExplanation,
    MitigationExplanation,
    RiskOverviewExplanation
)


class ExplanationController:
    """
    Controlador para operaciones de explicación científica
    
    Responsabilidades:
    - Generar explicaciones básicas de asteroides
    - Crear explicaciones de impacto comprensibles
    - Producir explicaciones de trayectoria orbital
    - Generar explicaciones de estrategias de mitigación
    - Crear resúmenes de riesgo general
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
    
    def get_asteroid_basic_explanation(self, neo_id: str) -> Optional[AsteroidBasicResponse]:
        """
        Genera explicación básica del asteroide
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Explicación básica del asteroide o None si no se encuentra
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Obtener datos del NEO
            cursor.execute("""
                SELECT n.*, np.confidence_score
                FROM neos n
                LEFT JOIN neo_predictions np ON n.neo_id = np.neo_id
                WHERE n.neo_id = %s
            """, (neo_id,))
            
            neo_data = cursor.fetchone()
            if not neo_data:
                return None
            
            cursor.close()
            conn.close()
            
            # Simular datos de entrada para el ExplainerAgent
            diameter_min = float(neo_data.get('estimated_diameter_min_m', 0))
            diameter_max = float(neo_data.get('estimated_diameter_max_m', 0))
            diameter_avg = (diameter_min + diameter_max) / 2
            
            asteroid_data = {
                'name': neo_data['name'],
                'diameter': diameter_avg,  # Diámetro promedio en metros
                'is_potentially_hazardous': neo_data.get('is_potentially_hazardous', False)
            }
            
            # Generar explicación usando el ExplainerAgent
            from ...agents.explainer_agent import ExplainerAgent
            explainer = ExplainerAgent()
            explanation_data = explainer._explain_asteroid_basics(asteroid_data)
            
            return AsteroidBasicResponse(
                neo_id=neo_id,
                neo_name=neo_data['name'],
                data=AsteroidBasicExplanation(**explanation_data),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando explicación básica: {e}")
            return None
    
    def get_impact_explanation(self, neo_id: str) -> Optional[ImpactExplanationResponse]:
        """
        Genera explicación de impacto
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Explicación de impacto o None si no se encuentra
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
            
            cursor.close()
            conn.close()
            
            # Simular datos de análisis de impacto
            impact_analysis = {
                'impact_energy': {'megatons': neo_data.get('impact_energy_mt', 0)},
                'crater_diameter_km': neo_data.get('crater_diameter_km', 0),
                'seismic_radius_km': neo_data.get('seismic_radius_km', 0),
                'tsunami_radius_km': neo_data.get('tsunami_radius_km', 0),
                'thermal_radius_km': neo_data.get('thermal_radius_km', 0),
                'blast_radius_km': neo_data.get('blast_radius_km', 0)
            }
            
            # Generar explicación usando el ExplainerAgent
            from ...agents.explainer_agent import ExplainerAgent
            explainer = ExplainerAgent()
            explanation_data = explainer._explain_impact(impact_analysis)
            
            return ImpactExplanationResponse(
                neo_id=neo_id,
                neo_name=neo_data['name'],
                data=ImpactExplanation(**explanation_data),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando explicación de impacto: {e}")
            return None
    
    def get_trajectory_explanation(self, neo_id: str) -> Optional[TrajectoryExplanationResponse]:
        """
        Genera explicación de trayectoria orbital
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Explicación de trayectoria o None si no se encuentra
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Obtener datos orbitales
            cursor.execute("""
                SELECT n.*, np.orbital_uncertainty, np.confidence_score
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
                LIMIT 1
            """, (neo_id,))
            
            approach_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            # Usar datos reales de aproximaciones cercanas
            if approach_data:
                trajectory_analysis = {
                    'orbital_period_days': 365,  # Valor por defecto
                    'semi_major_axis_au': 1.0,  # Valor por defecto
                    'eccentricity': 0.1,  # Valor por defecto
                    'inclination_deg': 5.0,  # Valor por defecto
                    'velocity_km_s': float(approach_data['relative_velocity_km_s']),
                    'closest_approach': {
                        'distance_km': float(approach_data['miss_distance_km']),
                        'date': approach_data['close_approach_date'].isoformat(),
                        'velocity_km_s': float(approach_data['relative_velocity_km_s'])
                    },
                    'confidence_metrics': {
                        'orbital_confidence': 1.0 - float(neo_data.get('orbital_uncertainty', 0.5))
                    }
                }
            else:
                # Fallback si no hay datos de aproximaciones
                trajectory_analysis = {
                    'orbital_period_days': 365,
                    'semi_major_axis_au': 1.0,
                    'eccentricity': 0.1,
                    'inclination_deg': 5.0,
                    'velocity_km_s': 30.0,
                    'closest_approach': {
                        'distance_km': 100000,
                        'date': '2024-12-31',
                        'velocity_km_s': 30.0
                    },
                    'confidence_metrics': {
                        'orbital_confidence': 0.5
                    }
                }
            
            # Generar explicación usando el ExplainerAgent
            from ...agents.explainer_agent import ExplainerAgent
            explainer = ExplainerAgent()
            explanation_data = explainer._explain_trajectory(trajectory_analysis)
            
            return TrajectoryExplanationResponse(
                neo_id=neo_id,
                neo_name=neo_data['name'],
                data=TrajectoryExplanation(**explanation_data),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando explicación de trayectoria: {e}")
            return None
    
    def get_mitigation_explanation(self, neo_id: str) -> Optional[MitigationExplanationResponse]:
        """
        Genera explicación de estrategias de mitigación
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Explicación de mitigación o None si no se encuentra
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Obtener datos del NEO
            cursor.execute("""
                SELECT n.*, np.mitigation_priority, np.analysis_confidence
                FROM neos n
                LEFT JOIN neo_predictions np ON n.neo_id = np.neo_id
                WHERE n.neo_id = %s
            """, (neo_id,))
            
            neo_data = cursor.fetchone()
            if not neo_data:
                return None
            
            cursor.close()
            conn.close()
            
            # Simular datos de análisis de mitigación
            mitigation_analysis = {
                'strategies': [
                    {'name': 'Deflector cinético', 'feasibility': 'Alta', 'cost': 1000000000},
                    {'name': 'Tractor gravitacional', 'feasibility': 'Media', 'cost': 5000000000},
                    {'name': 'Explosión nuclear', 'feasibility': 'Baja', 'cost': 2000000000}
                ],
                'priority': neo_data.get('mitigation_priority', 'Media'),
                'confidence': neo_data.get('analysis_confidence', 0.5)
            }
            
            # Generar explicación usando el ExplainerAgent
            from ...agents.explainer_agent import ExplainerAgent
            explainer = ExplainerAgent()
            explanation_data = explainer._explain_mitigation(mitigation_analysis)
            
            return MitigationExplanationResponse(
                neo_id=neo_id,
                neo_name=neo_data['name'],
                data=MitigationExplanation(**explanation_data),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando explicación de mitigación: {e}")
            return None
    
    def get_risk_overview(self, neo_id: str) -> Optional[RiskOverviewResponse]:
        """
        Genera resumen general de riesgo
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Resumen de riesgo o None si no se encuentra
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Obtener datos del NEO
            cursor.execute("""
                SELECT n.*, np.risk_score, np.confidence_score, np.analysis_confidence
                FROM neos n
                LEFT JOIN neo_predictions np ON n.neo_id = np.neo_id
                WHERE n.neo_id = %s
            """, (neo_id,))
            
            neo_data = cursor.fetchone()
            if not neo_data:
                return None
            
            cursor.close()
            conn.close()
            
            # Simular datos para el resumen de riesgo
            diameter_min = float(neo_data.get('estimated_diameter_min_m', 0))
            diameter_max = float(neo_data.get('estimated_diameter_max_m', 0))
            diameter_avg = (diameter_min + diameter_max) / 2
            
            asteroid_data = {
                'name': neo_data['name'],
                'diameter': diameter_avg,
                'is_potentially_hazardous': neo_data.get('is_potentially_hazardous', False)
            }
            
            trajectory_analysis = {
                'orbital_period_days': 365,
                'eccentricity': 0.1,
                'closest_approach': {'distance_km': 100000}
            }
            
            impact_analysis = {
                'impact_energy': {'megatons': neo_data.get('impact_energy_mt', 0)},
                'crater_diameter_km': neo_data.get('crater_diameter_km', 0)
            }
            
            # Generar explicación usando el ExplainerAgent
            from ...agents.explainer_agent import ExplainerAgent
            explainer = ExplainerAgent()
            explanation_data = explainer._explain_risk_overview(asteroid_data, trajectory_analysis, impact_analysis)
            
            return RiskOverviewResponse(
                neo_id=neo_id,
                neo_name=neo_data['name'],
                data=RiskOverviewExplanation(**explanation_data),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando resumen de riesgo: {e}")
            return None
    
    def get_complete_explanation(self, neo_id: str) -> Optional[CompleteExplanationResponse]:
        """
        Genera explicación completa del asteroide
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Explicación completa o None si no se encuentra
        """
        try:
            # Obtener todas las explicaciones
            asteroid_basics = self.get_asteroid_basic_explanation(neo_id)
            impact_analysis = self.get_impact_explanation(neo_id)
            trajectory_analysis = self.get_trajectory_explanation(neo_id)
            mitigation_analysis = self.get_mitigation_explanation(neo_id)
            risk_overview = self.get_risk_overview(neo_id)
            
            if not asteroid_basics:
                return None
            
            return CompleteExplanationResponse(
                neo_id=neo_id,
                neo_name=asteroid_basics.neo_name,
                asteroid_basics=asteroid_basics.data,
                impact_analysis=impact_analysis.data if impact_analysis else None,
                trajectory_analysis=trajectory_analysis.data if trajectory_analysis else None,
                mitigation_analysis=mitigation_analysis.data if mitigation_analysis else None,
                risk_overview=risk_overview.data if risk_overview else None,
                generated_at=datetime.utcnow(),
                confidence_score=0.8  # Valor por defecto
            )
            
        except Exception as e:
            print(f"Error generando explicación completa: {e}")
            return None