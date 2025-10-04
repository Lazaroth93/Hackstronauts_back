"""
Advanced Prediction Agent para predicciones avanzadas de impacto
Integrado desde workspace/prototipo1/agents/neo_prediction_agent/
"""

import os
import time
import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from .base_agent import BaseAgent, AgentState

logger = logging.getLogger(__name__)

class AdvancedPredictionAgent(BaseAgent):
    """
    Agente de Predicción Avanzada para análisis de impacto y predicciones
    de asteroides usando técnicas de machine learning
    """
    
    def __init__(self):
        super().__init__()
        self.name = "AdvancedPredictionAgent"
        self.description = "Agente de Predicción Avanzada para análisis de impacto"
        self.database_url = os.getenv("DATABASE_URL")
    
    def _get_connection(self, retries: int = 5, delay: int = 5):
        """Intentos de conexión a la base de datos con reintentos."""
        for i in range(retries):
            try:
                conn = psycopg2.connect(
                    self.database_url, 
                    cursor_factory=psycopg2.extras.RealDictCursor
                )
                return conn
            except psycopg2.OperationalError:
                logger.warning(f"[Advanced Prediction Agent] DB no disponible, reintentando ({i+1}/{retries})...")
                time.sleep(delay)
        raise Exception("[Advanced Prediction Agent] No se pudo conectar a la DB")
    
    def _predict_impact(self) -> Dict[str, Any]:
        """Realiza predicciones avanzadas de impacto para NEOs peligrosos"""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            logger.info("[Advanced Impact Prediction Agent] Iniciando análisis completo...")
            
            # Obtener NEOs peligrosos
            cur.execute(
                "SELECT * FROM neos_dangerous WHERE is_potentially_hazardous = TRUE;"
            )
            rows = cur.fetchall()
            
            if not rows:
                logger.warning("[Advanced Impact Prediction Agent] No hay NEOs peligrosos para analizar")
                return self._get_empty_predictions()
            
            df = pd.DataFrame(rows)
            logger.info(f"[Advanced Impact Prediction Agent] Analizando {len(df)} NEOs peligrosos")
            
            # === CÁLCULO DE PROPIEDADES FÍSICAS ===
            df["avg_diameter"] = df[["diameter_min_m", "diameter_max_m"]].mean(axis=1)
            df["density"] = 3000  # kg/m³ base (asteroides rocosos)
            
            # Calcular masa y volumen
            df["volume"] = (4/3) * np.pi * (df["avg_diameter"] / 2) ** 3
            df["mass_kg"] = df["density"] * df["volume"]
            
            # === ANÁLISIS DE ENERGÍA CINÉTICA ===
            df["kinetic_energy_j"] = 0.5 * df["mass_kg"] * (df["velocity_km_s"] * 1000) ** 2
            df["kinetic_energy_mt_tnt"] = df["kinetic_energy_j"] / (4.184e15)  # Conversión a MT TNT
            
            # === PREDICCIÓN DE PROBABILIDAD DE IMPACTO ===
            # Basado en distancia de fallo y velocidad
            df["impact_probability"] = 1 / (1 + (df["miss_distance_km"] / 1000000))
            
            # === PREDICCIÓN DE EFECTOS DEL IMPACTO ===
            df["crater_diameter_km"] = 0.1 * (df["kinetic_energy_mt_tnt"] ** 0.3)
            df["damage_radius_km"] = 2.5 * (df["kinetic_energy_mt_tnt"] ** 0.33)
            df["seismic_magnitude"] = 0.67 * np.log10(df["kinetic_energy_mt_tnt"]) + 4.0
            
            # === CLASIFICACIÓN DE RIESGO ===
            def classify_risk(row):
                if row["kinetic_energy_mt_tnt"] > 1000 and row["impact_probability"] > 0.01:
                    return "Extreme"
                elif row["kinetic_energy_mt_tnt"] > 100 and row["impact_probability"] > 0.001:
                    return "High"
                elif row["kinetic_energy_mt_tnt"] > 10 and row["impact_probability"] > 0.0001:
                    return "Medium"
                else:
                    return "Low"
            
            df["risk_level"] = df.apply(classify_risk, axis=1)
            
            # === PREDICCIONES TEMPORALES ===
            predictions = []
            for _, row in df.iterrows():
                prediction = {
                    "neo_id": row["neo_id"],
                    "name": row["name"],
                    "physical_properties": {
                        "diameter_avg_m": float(row["avg_diameter"]),
                        "mass_kg": float(row["mass_kg"]),
                        "density_kg_m3": float(row["density"]),
                        "velocity_km_s": float(row["velocity_km_s"])
                    },
                    "impact_analysis": {
                        "kinetic_energy_j": float(row["kinetic_energy_j"]),
                        "kinetic_energy_mt_tnt": float(row["kinetic_energy_mt_tnt"]),
                        "impact_probability": float(row["impact_probability"]),
                        "crater_diameter_km": float(row["crater_diameter_km"]),
                        "damage_radius_km": float(row["damage_radius_km"]),
                        "seismic_magnitude": float(row["seismic_magnitude"])
                    },
                    "risk_assessment": {
                        "risk_level": row["risk_level"],
                        "monitoring_priority": "High" if row["risk_level"] in ["Extreme", "High"] else "Medium",
                        "evacuation_radius_km": float(row["damage_radius_km"]),
                        "tsunami_risk": "High" if row["kinetic_energy_mt_tnt"] > 10 and row["miss_distance_km"] < 1000000 else "Low"
                    },
                    "temporal_predictions": self._generate_temporal_predictions(row),
                    "confidence_score": self._calculate_confidence_score(row)
                }
                predictions.append(prediction)
            
            # Almacenar predicciones en la base de datos
            self._store_predictions(predictions)
            
            # Resumen estadístico
            summary = {
                "total_analyzed": len(df),
                "risk_distribution": df["risk_level"].value_counts().to_dict(),
                "avg_impact_probability": float(df["impact_probability"].mean()),
                "max_kinetic_energy_mt": float(df["kinetic_energy_mt_tnt"].max()),
                "high_risk_count": int((df["risk_level"].isin(["High", "Extreme"])).sum()),
                "predictions": predictions,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"[Advanced Impact Prediction Agent] Análisis completado - {len(predictions)} predicciones generadas")
            return summary
            
        except Exception as e:
            logger.error(f"[Advanced Impact Prediction Agent] Error en predicción: {e}")
            return self._get_empty_predictions()
        finally:
            cur.close()
            conn.close()
    
    def _get_empty_predictions(self) -> Dict[str, Any]:
        """Retorna predicciones vacías cuando no hay datos"""
        return {
            "total_analyzed": 0,
            "risk_distribution": {},
            "avg_impact_probability": 0.0,
            "max_kinetic_energy_mt": 0.0,
            "high_risk_count": 0,
            "predictions": [],
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_temporal_predictions(self, row: pd.Series) -> Dict[str, Any]:
        """Genera predicciones temporales para un NEO específico"""
        # Simular predicciones para los próximos 10 años
        years = list(range(1, 11))
        predictions = []
        
        for year in years:
            # Simular evolución de la probabilidad de impacto
            base_prob = row["impact_probability"]
            time_factor = 1 + (year * 0.1)  # Aumenta con el tiempo
            predicted_prob = min(1.0, base_prob * time_factor)
            
            # Simular evolución de la energía cinética
            energy_factor = 1 + (year * 0.05)  # Ligero aumento
            predicted_energy = row["kinetic_energy_mt_tnt"] * energy_factor
            
            predictions.append({
                "year": year,
                "impact_probability": float(predicted_prob),
                "kinetic_energy_mt_tnt": float(predicted_energy),
                "confidence": max(0.5, 1.0 - (year * 0.05))  # Disminuye con el tiempo
            })
        
        return {
            "temporal_predictions": predictions,
            "trend": "increasing" if predictions[-1]["impact_probability"] > predictions[0]["impact_probability"] else "decreasing",
            "peak_year": max(predictions, key=lambda x: x["impact_probability"])["year"]
        }
    
    def _calculate_confidence_score(self, row: pd.Series) -> float:
        """Calcula un score de confianza para las predicciones"""
        # Factores que afectan la confianza
        data_completeness = 1.0  # Asumimos datos completos
        velocity_confidence = min(1.0, row["velocity_km_s"] / 50.0)  # Velocidades altas son más inciertas
        distance_confidence = min(1.0, row["miss_distance_km"] / 1000000)  # Distancias grandes son más inciertas
        
        # Score combinado
        confidence = (data_completeness + velocity_confidence + distance_confidence) / 3.0
        return min(1.0, max(0.1, confidence))
    
    def _store_predictions(self, predictions: List[Dict[str, Any]]) -> bool:
        """Almacena predicciones en la base de datos"""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            # Crear tabla si no existe
            cur.execute("""
            CREATE TABLE IF NOT EXISTS advanced_predictions (
                id SERIAL PRIMARY KEY,
                neo_id VARCHAR(64) NOT NULL,
                prediction_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Insertar predicciones
            for prediction in predictions:
                cur.execute("""
                INSERT INTO advanced_predictions (neo_id, prediction_data)
                VALUES (%s, %s)
                """, (prediction["neo_id"], json.dumps(prediction)))
            
            conn.commit()
            logger.info(f"[Advanced Prediction Agent] {len(predictions)} predicciones almacenadas")
            return True
            
        except Exception as e:
            logger.error(f"[Advanced Prediction Agent] Error almacenando predicciones: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Ejecuta el agente de predicción avanzada
        """
        try:
            logger.info(f"[Advanced Prediction Agent] Iniciando predicciones avanzadas...")
            
            # Realizar predicciones de impacto
            predictions = self._predict_impact()
            
            # Actualizar estado
            state.advanced_predictions = predictions
            
            logger.info(f"[Advanced Prediction Agent] Predicciones completadas exitosamente")
            return state
            
        except Exception as e:
            logger.error(f"[Advanced Prediction Agent] Error en predicciones: {e}")
            state.advanced_predictions = {
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
            return state
