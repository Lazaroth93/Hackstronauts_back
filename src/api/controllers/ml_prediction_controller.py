"""
Controlador para Predicciones ML
Contiene la lógica de negocio para generar predicciones de machine learning
"""

import os
import psycopg2
import psycopg2.extras
from typing import Dict, Any, Optional
from datetime import datetime

from ..models.ml_prediction_models import (
    CompleteMLPredictionResponse,
    TrajectoryPredictionAPIResponse,
    RiskEvolutionAPIResponse,
    ImpactProbabilityAPIResponse,
    HistoricalAnalysisAPIResponse,
    ModelConfidenceAPIResponse,
    TrajectoryPredictionResponse,
    RiskEvolutionResponse,
    ImpactProbabilityResponse,
    HistoricalAnalysisResponse,
    ModelConfidenceResponse
)


class MLPredictionController:
    """
    Controlador para operaciones de predicciones ML
    
    Responsabilidades:
    - Generar predicciones de trayectoria futura
    - Crear análisis de evolución de riesgo temporal
    - Producir probabilidades de impacto ML
    - Generar análisis de patrones históricos
    - Calcular confianza de modelos ML
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
    
    def get_trajectory_prediction(self, neo_id: str) -> Optional[TrajectoryPredictionAPIResponse]:
        """
        Genera predicción de trayectoria futura
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Predicción de trayectoria o None si no se encuentra
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Obtener datos del NEO
            cursor.execute("""
                SELECT n.*, np.orbital_uncertainty, np.confidence_score
                FROM neos n
                LEFT JOIN neo_predictions np ON n.neo_id = np.neo_id
                WHERE n.neo_id = %s
            """, (neo_id,))
            
            neo_data = cursor.fetchone()
            if not neo_data:
                return None
            
            cursor.close()
            conn.close()
            
            # Simular datos de análisis de trayectoria
            trajectory_analysis = {
                'orbital_period_days': 365,  # Valor por defecto
                'eccentricity': 0.1,  # Valor por defecto
                'closest_approach': {
                    'distance_km': 100000,
                    'date': '2024-12-31',
                    'velocity_km_s': 30.0
                }
            }
            
            # Generar predicción usando el MLPredictorAgent
            from ...agents.ml_predictor_agent import MLPredictorAgent
            ml_predictor = MLPredictorAgent()
            prediction_data = ml_predictor._predict_future_trajectory(trajectory_analysis, neo_data)
            
            return TrajectoryPredictionAPIResponse(
                neo_id=neo_id,
                neo_name=neo_data['name'],
                data=TrajectoryPredictionResponse(**prediction_data),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando predicción de trayectoria: {e}")
            return None
    
    def get_risk_evolution(self, neo_id: str) -> Optional[RiskEvolutionAPIResponse]:
        """
        Genera análisis de evolución de riesgo temporal
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Evolución de riesgo o None si no se encuentra
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
            
            cursor.close()
            conn.close()
            
            # Simular datos para análisis de riesgo
            diameter_min = float(neo_data.get('estimated_diameter_min_m', 0))
            diameter_max = float(neo_data.get('estimated_diameter_max_m', 0))
            diameter_avg = (diameter_min + diameter_max) / 2
            
            asteroid_data = {
                'name': neo_data['name'],
                'diameter': diameter_avg,
                'is_potentially_hazardous': neo_data.get('is_potentially_hazardous', False)
            }
            
            trajectory_analysis = {
                'eccentricity': 0.1,
                'closest_approach': {'distance_km': 100000}
            }
            
            impact_analysis = {
                'impact_energy': {'megatons': neo_data.get('impact_energy_mt', 0)},
                'crater_diameter_km': neo_data.get('crater_diameter_km', 0)
            }
            
            # Generar predicción usando el MLPredictorAgent
            from ...agents.ml_predictor_agent import MLPredictorAgent
            ml_predictor = MLPredictorAgent()
            prediction_data = ml_predictor._predict_risk_evolution(asteroid_data, trajectory_analysis, impact_analysis)
            
            return RiskEvolutionAPIResponse(
                neo_id=neo_id,
                neo_name=neo_data['name'],
                data=RiskEvolutionResponse(**prediction_data),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando evolución de riesgo: {e}")
            return None
    
    def get_impact_probability(self, neo_id: str) -> Optional[ImpactProbabilityAPIResponse]:
        """
        Genera probabilidades de impacto ML
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Probabilidades de impacto o None si no se encuentra
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Obtener datos del NEO
            cursor.execute("""
                SELECT n.*, np.impact_probability, np.confidence_score
                FROM neos n
                LEFT JOIN neo_predictions np ON n.neo_id = np.neo_id
                WHERE n.neo_id = %s
            """, (neo_id,))
            
            neo_data = cursor.fetchone()
            if not neo_data:
                return None
            
            cursor.close()
            conn.close()
            
            # Simular datos para análisis de impacto
            asteroid_data = {
                'name': neo_data['name'],
                'diameter': neo_data.get('diameter_km', 0) * 1000,
                'is_potentially_hazardous': neo_data.get('is_potentially_hazardous', False)
            }
            
            trajectory_analysis = {
                'eccentricity': 0.1,
                'closest_approach': {'distance_km': 100000}
            }
            
            impact_analysis = {
                'impact_energy': {'megatons': neo_data.get('impact_energy_mt', 0)},
                'crater_diameter_km': neo_data.get('crater_diameter_km', 0)
            }
            
            # Generar predicción usando el MLPredictorAgent
            from ...agents.ml_predictor_agent import MLPredictorAgent
            ml_predictor = MLPredictorAgent()
            prediction_data = ml_predictor._predict_impact_probability(asteroid_data, trajectory_analysis, impact_analysis)
            
            return ImpactProbabilityAPIResponse(
                neo_id=neo_id,
                neo_name=neo_data['name'],
                data=ImpactProbabilityResponse(**prediction_data),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando probabilidad de impacto: {e}")
            return None
    
    def get_historical_analysis(self, neo_id: str) -> Optional[HistoricalAnalysisAPIResponse]:
        """
        Genera análisis de patrones históricos
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Análisis histórico o None si no se encuentra
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
            
            # Simular datos para análisis histórico
            diameter_min = float(neo_data.get('estimated_diameter_min_m', 0))
            diameter_max = float(neo_data.get('estimated_diameter_max_m', 0))
            diameter_avg = (diameter_min + diameter_max) / 2
            
            asteroid_data = {
                'name': neo_data['name'],
                'diameter': diameter_avg,
                'is_potentially_hazardous': neo_data.get('is_potentially_hazardous', False)
            }
            
            trajectory_analysis = {
                'eccentricity': 0.1,
                'orbital_period_days': 365
            }
            
            # Generar análisis usando el MLPredictorAgent
            from ...agents.ml_predictor_agent import MLPredictorAgent
            ml_predictor = MLPredictorAgent()
            analysis_data = ml_predictor._analyze_historical_patterns(asteroid_data, trajectory_analysis)
            
            return HistoricalAnalysisAPIResponse(
                neo_id=neo_id,
                neo_name=neo_data['name'],
                data=HistoricalAnalysisResponse(**analysis_data),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando análisis histórico: {e}")
            return None
    
    def get_model_confidence(self, neo_id: str) -> Optional[ModelConfidenceAPIResponse]:
        """
        Genera análisis de confianza del modelo ML
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Confianza del modelo o None si no se encuentra
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Obtener datos del NEO
            cursor.execute("""
                SELECT n.*, np.confidence_score, np.analysis_confidence
                FROM neos n
                LEFT JOIN neo_predictions np ON n.neo_id = np.neo_id
                WHERE n.neo_id = %s
            """, (neo_id,))
            
            neo_data = cursor.fetchone()
            if not neo_data:
                return None
            
            cursor.close()
            conn.close()
            
            # Simular predicciones para calcular confianza
            mock_predictions = {
                "trajectory_prediction": {"confidence_overall": 0.8},
                "risk_prediction": {"risk_evolution": [{"confidence": 0.7} for _ in range(10)]},
                "impact_probability": {},
                "historical_analysis": {}
            }
            
            # Generar análisis usando el MLPredictorAgent
            from ...agents.ml_predictor_agent import MLPredictorAgent
            ml_predictor = MLPredictorAgent()
            confidence_data = ml_predictor._calculate_model_confidence(mock_predictions)
            
            return ModelConfidenceAPIResponse(
                neo_id=neo_id,
                neo_name=neo_data['name'],
                data=ModelConfidenceResponse(**confidence_data),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando confianza del modelo: {e}")
            return None
    
    def get_complete_ml_prediction(self, neo_id: str) -> Optional[CompleteMLPredictionResponse]:
        """
        Genera predicciones ML completas del asteroide
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Predicciones ML completas o None si no se encuentra
        """
        try:
            # Obtener todas las predicciones
            trajectory_prediction = self.get_trajectory_prediction(neo_id)
            risk_evolution = self.get_risk_evolution(neo_id)
            impact_probability = self.get_impact_probability(neo_id)
            historical_analysis = self.get_historical_analysis(neo_id)
            model_confidence = self.get_model_confidence(neo_id)
            
            if not trajectory_prediction:
                return None
            
            return CompleteMLPredictionResponse(
                neo_id=neo_id,
                neo_name=trajectory_prediction.neo_name,
                trajectory_prediction=trajectory_prediction.data,
                risk_prediction=risk_evolution.data if risk_evolution else None,
                impact_probability=impact_probability.data if impact_probability else None,
                historical_analysis=historical_analysis.data if historical_analysis else None,
                model_confidence=model_confidence.data if model_confidence else None,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generando predicciones ML completas: {e}")
            return None