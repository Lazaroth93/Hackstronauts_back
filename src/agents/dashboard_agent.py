"""
Dashboard Agent para generación de métricas y análisis estadístico
Integrado desde workspace/prototipo1/agents/neo_dashboard_agent/
"""

import os
import time
import psycopg2
import psycopg2.extras
import pandas as pd
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .base_agent import BaseAgent, AgentState

logger = logging.getLogger(__name__)

class DashboardAgent(BaseAgent):
    """
    Agente Dashboard para generación de métricas y análisis estadístico
    de datos de asteroides
    """
    
    def __init__(self):
        super().__init__()
        self.name = "DashboardAgent"
        self.description = "Agente Dashboard para generación de métricas y análisis estadístico"
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
                logger.warning(f"[Dashboard Agent] DB no disponible, reintentando ({i+1}/{retries})...")
                time.sleep(delay)
        raise Exception("[Dashboard Agent] No se pudo conectar a la DB")
    
    def _generate_metrics(self) -> Dict[str, Any]:
        """Genera métricas del dashboard basadas en datos de NEOs"""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            logger.info("[Dashboard Agent] Consultando NEOs peligrosos...")
            
            # Consultar NEOs peligrosos
            cur.execute(
                "SELECT * FROM neos_dangerous WHERE is_potentially_hazardous = TRUE;"
            )
            rows = cur.fetchall()
            
            if not rows:
                logger.warning("[Dashboard Agent] No hay NEOs peligrosos")
                return self._get_empty_metrics()
            
            df = pd.DataFrame(rows)
            logger.info(f"[Dashboard Agent] Encontrados {len(df)} NEOs peligrosos")
            
            # Calcular métricas
            total_neos = len(df)
            avg_velocity = df["velocity_km_s"].mean() if "velocity_km_s" in df.columns else 0
            avg_diameter = df[["diameter_min_m", "diameter_max_m"]].mean().mean() if "diameter_min_m" in df.columns else 0
            
            metrics = {
                "total_dangerous_neos": int(total_neos),
                "average_velocity_km_s": float(avg_velocity) if not pd.isna(avg_velocity) else 0.0,
                "average_diameter_m": float(avg_diameter) if not pd.isna(avg_diameter) else 0.0,
                "max_velocity_km_s": float(df["velocity_km_s"].max()) if "velocity_km_s" in df.columns and not pd.isna(df["velocity_km_s"].max()) else 0.0,
                "min_velocity_km_s": float(df["velocity_km_s"].min()) if "velocity_km_s" in df.columns and not pd.isna(df["velocity_km_s"].min()) else 0.0,
                "max_diameter_m": float(df[["diameter_min_m", "diameter_max_m"]].max().max()) if "diameter_min_m" in df.columns and not pd.isna(df[["diameter_min_m", "diameter_max_m"]].max().max()) else 0.0,
                "min_diameter_m": float(df[["diameter_min_m", "diameter_max_m"]].min().min()) if "diameter_min_m" in df.columns and not pd.isna(df[["diameter_min_m", "diameter_max_m"]].min().min()) else 0.0,
                "generated_at": datetime.now().isoformat()
            }
            
            # Almacenar métricas en la base de datos
            self._store_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"[Dashboard Agent] Error generando métricas: {e}")
            return self._get_empty_metrics()
        finally:
            cur.close()
            conn.close()
    
    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Retorna métricas vacías cuando no hay datos"""
        return {
            "total_dangerous_neos": 0,
            "average_velocity_km_s": 0.0,
            "average_diameter_m": 0.0,
            "max_velocity_km_s": 0.0,
            "min_velocity_km_s": 0.0,
            "max_diameter_m": 0.0,
            "min_diameter_m": 0.0,
            "generated_at": datetime.now().isoformat()
        }
    
    def _store_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Almacena métricas en la base de datos"""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            # Crear tabla si no existe
            cur.execute("""
            CREATE TABLE IF NOT EXISTS dashboard_results (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(255) NOT NULL,
                value DECIMAL(15,6) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Insertar métricas
            for metric_name, value in metrics.items():
                if metric_name != "generated_at" and isinstance(value, (int, float)):
                    cur.execute("""
                    INSERT INTO dashboard_results (metric_name, value)
                    VALUES (%s, %s)
                    """, (metric_name, value))
            
            conn.commit()
            logger.info("[Dashboard Agent] Métricas almacenadas en la base de datos")
            return True
            
        except Exception as e:
            logger.error(f"[Dashboard Agent] Error almacenando métricas: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()
    
    def _get_historical_metrics(self, days: int = 7) -> List[Dict[str, Any]]:
        """Obtiene métricas históricas de los últimos N días"""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            cur.execute("""
            SELECT metric_name, value, created_at
            FROM dashboard_results
            WHERE created_at >= NOW() - INTERVAL '%s days'
            ORDER BY created_at DESC
            """, (days,))
            
            results = cur.fetchall()
            logger.info(f"[Dashboard Agent] Obtenidas {len(results)} métricas históricas")
            return results
            
        except Exception as e:
            logger.error(f"[Dashboard Agent] Error obteniendo métricas históricas: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    def _analyze_trends(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analiza tendencias en los datos históricos"""
        if not historical_data:
            return {"trends": "No hay datos históricos disponibles"}
        
        # Convertir a DataFrame para análisis
        df = pd.DataFrame(historical_data)
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        trends = {}
        
        # Agrupar por métrica y calcular tendencias
        for metric_name in df['metric_name'].unique():
            metric_data = df[df['metric_name'] == metric_name].copy()
            metric_data = metric_data.sort_values('created_at')
            
            if len(metric_data) > 1:
                # Calcular tendencia simple (pendiente)
                x = range(len(metric_data))
                y = metric_data['value'].values
                
                # Regresión lineal simple
                n = len(x)
                sum_x = sum(x)
                sum_y = sum(y)
                sum_xy = sum(x[i] * y[i] for i in range(n))
                sum_x2 = sum(x[i] ** 2 for i in range(n))
                
                if n * sum_x2 - sum_x ** 2 != 0:
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
                    trends[metric_name] = {
                        "trend": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                        "slope": float(slope),
                        "latest_value": float(metric_data['value'].iloc[-1]),
                        "data_points": len(metric_data)
                    }
                else:
                    trends[metric_name] = {
                        "trend": "stable",
                        "slope": 0.0,
                        "latest_value": float(metric_data['value'].iloc[-1]),
                        "data_points": len(metric_data)
                    }
        
        return {"trends": trends}
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Ejecuta el agente Dashboard para generar métricas y análisis
        """
        try:
            logger.info(f"[Dashboard Agent] Iniciando generación de métricas...")
            
            # Generar métricas actuales
            current_metrics = self._generate_metrics()
            
            # Obtener métricas históricas
            historical_data = self._get_historical_metrics(days=7)
            
            # Analizar tendencias
            trend_analysis = self._analyze_trends(historical_data)
            
            # Crear resumen del dashboard
            dashboard_summary = {
                "current_metrics": current_metrics,
                "historical_data": historical_data,
                "trend_analysis": trend_analysis,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
            # Actualizar estado
            state.dashboard_metrics = dashboard_summary
            
            logger.info(f"[Dashboard Agent] Métricas generadas exitosamente")
            return state
            
        except Exception as e:
            logger.error(f"[Dashboard Agent] Error generando métricas: {e}")
            state.dashboard_metrics = {
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
            return state
