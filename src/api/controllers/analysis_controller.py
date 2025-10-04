"""
Controlador para Análisis de Asteroides con LangGraph
Contiene la lógica de negocio para análisis con IA
Siguiendo principios SOLID - Responsabilidad única
"""

import os
import psycopg2
import psycopg2.extras
from typing import Optional, Dict, Any
from datetime import datetime
import math

from ..models.analysis_models import (
    PhysicalProperties,
    AsteroidAnalysisResponse,
    ConfidenceMetricsResponse,
    ImpactPredictionResponse,
    HybridAnalysisRequest,
    HybridAnalysisResponse,
    ImpactAnalysis,
    RiskFactors,
    RiskAssessment,
    DataQuality,
    PredictionReliability,
    HybridAnalysisSummary
)


class AnalysisController:
    """
    Controlador para análisis de asteroides usando LangGraph
    
    Responsabilidades:
    - Analizar propiedades físicas de asteroides
    - Calcular métricas de impacto
    - Evaluar factores de riesgo
    - Generar predicciones de impacto
    - Realizar análisis híbridos
    - Calcular métricas de confianza
    """
    
    def __init__(self):
        """Inicializa la conexión a la base de datos"""
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL no está configurada")
    
    def _get_connection(self):
        """
        Obtiene una conexión a la base de datos
        
        Returns:
            psycopg2.connection: Conexión a PostgreSQL
        """
        return psycopg2.connect(
            self.database_url, 
            cursor_factory=psycopg2.extras.RealDictCursor
        )
    
    def analyze_asteroid(self, physical_properties: PhysicalProperties) -> AsteroidAnalysisResponse:
        """
        Analiza un asteroide usando cálculos físicos y modelos de riesgo
        
        Args:
            physical_properties: Propiedades físicas del asteroide
            
        Returns:
            AsteroidAnalysisResponse: Análisis completo del asteroide
        """
        try:
            # Calcular propiedades derivadas
            diameter_avg = (physical_properties.diameter_m) / 2
            volume = (4/3) * math.pi * (diameter_avg/2)**3
            mass_calculated = physical_properties.density_kg_m3 * volume
            
            # Calcular energía cinética
            kinetic_energy = 0.5 * mass_calculated * (physical_properties.velocity_km_s * 1000)**2
            
            # Calcular análisis de impacto
            impact_analysis = self._calculate_impact_analysis(
                physical_properties, kinetic_energy
            )
            
            # Evaluar factores de riesgo
            risk_factors = self._evaluate_risk_factors(physical_properties)
            
            # Realizar evaluación de riesgo
            risk_assessment = self._assess_risk(risk_factors, impact_analysis)
            
            # Evaluar calidad de datos
            data_quality = self._assess_data_quality(physical_properties)
            
            return AsteroidAnalysisResponse(
                asteroid_id=f"AST_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                physical_properties=physical_properties,
                impact_analysis=impact_analysis,
                risk_factors=risk_factors,
                risk_assessment=risk_assessment,
                data_quality=data_quality,
                analysis_timestamp=datetime.utcnow(),
                confidence_score=self._calculate_confidence_score(data_quality, risk_factors)
            )
            
        except Exception as e:
            raise Exception(f"Error en análisis del asteroide: {str(e)}")
    
    def get_confidence_metrics(self, neo_id: str) -> Optional[ConfidenceMetricsResponse]:
        """
        Obtiene métricas de confianza para un NEO específico
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            ConfidenceMetricsResponse o None si no se encuentra
        """
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            # Obtener datos del NEO
            cur.execute("""
            SELECT 
                nd.*,
                np.risk_score,
                NULL as risk_category,
                np.created_at as prediction_date
            FROM neos_dangerous nd
            LEFT JOIN neo_predictions np ON nd.neo_id = np.neo_id
            WHERE nd.neo_id = %s
            ORDER BY np.created_at DESC
            LIMIT 1
            """, (neo_id,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            # Evaluar calidad de datos
            data_quality = self._assess_neo_data_quality(row)
            
            # Calcular confiabilidad de predicciones
            prediction_reliability = self._calculate_prediction_reliability(row)
            
            return ConfidenceMetricsResponse(
                neo_id=neo_id,
                data_quality=data_quality,
                prediction_reliability=prediction_reliability,
                overall_confidence=self._calculate_overall_confidence(data_quality, prediction_reliability),
                recommendations=self._generate_recommendations(data_quality, prediction_reliability),
                last_updated=datetime.utcnow()
            )
            
        finally:
            cur.close()
            conn.close()
    
    def predict_impact(self, physical_properties: PhysicalProperties) -> ImpactPredictionResponse:
        """
        Predice el impacto de un asteroide en la Tierra
        
        Args:
            physical_properties: Propiedades físicas del asteroide
            
        Returns:
            ImpactPredictionResponse: Predicción de impacto
        """
        try:
            # Calcular energía cinética
            diameter_avg = physical_properties.diameter_m
            volume = (4/3) * math.pi * (diameter_avg/2)**3
            mass = physical_properties.density_kg_m3 * volume
            kinetic_energy = 0.5 * mass * (physical_properties.velocity_km_s * 1000)**2
            
            # Calcular análisis de impacto
            impact_analysis = self._calculate_impact_analysis(
                physical_properties, kinetic_energy
            )
            
            # Calcular probabilidad de impacto (simplificada)
            impact_probability = self._calculate_impact_probability(physical_properties)
            
            # Determinar categoría de riesgo
            risk_category = self._determine_risk_category(impact_analysis, impact_probability)
            
            return ImpactPredictionResponse(
                prediction_id=f"IMP_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                physical_properties=physical_properties,
                impact_analysis=impact_analysis,
                impact_probability=impact_probability,
                risk_category=risk_category,
                prediction_timestamp=datetime.utcnow(),
                confidence_level=self._calculate_prediction_confidence(physical_properties)
            )
            
        except Exception as e:
            raise Exception(f"Error en predicción de impacto: {str(e)}")
    
    def hybrid_analysis(self, analysis_request: HybridAnalysisRequest) -> HybridAnalysisResponse:
        """
        Realiza análisis híbrido combinando múltiples fuentes de datos
        
        Args:
            analysis_request: Parámetros del análisis híbrido
            
        Returns:
            HybridAnalysisResponse: Análisis híbrido completo
        """
        start_time = datetime.utcnow()
        
        try:
            results = {}
            
            # Análisis básico de propiedades físicas
            if analysis_request.physical_properties:
                results["physical_analysis"] = self.analyze_asteroid(
                    analysis_request.physical_properties
                )
            
            # Análisis de NEO específico si se proporciona ID
            if analysis_request.neo_id:
                results["neo_analysis"] = self.get_confidence_metrics(analysis_request.neo_id)
            
            # Predicción de impacto si se solicita
            if analysis_request.include_predictions and analysis_request.physical_properties:
                results["impact_prediction"] = self.predict_impact(
                    analysis_request.physical_properties
                )
            
            # Crear resumen del análisis
            summary = self._create_hybrid_summary(results, analysis_request)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return HybridAnalysisResponse(
                analysis_id=f"HYB_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                summary=summary,
                detailed_results=results,
                processing_time_seconds=processing_time,
                analysis_timestamp=start_time,
                recommendations=self._generate_hybrid_recommendations(results)
            )
            
        except Exception as e:
            raise Exception(f"Error en análisis híbrido: {str(e)}")
    
    def get_service_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del servicio de análisis
        
        Returns:
            Dict con estadísticas del servicio
        """
        return {
            "total_analyses": 0,  # Se puede implementar contador en BD
            "avg_processing_time": 0.5,  # Tiempo promedio en segundos
            "service_uptime": "100%",
            "last_analysis": datetime.utcnow().isoformat()
        }
    
    def _calculate_impact_analysis(self, props: PhysicalProperties, kinetic_energy: float) -> ImpactAnalysis:
        """Calcula análisis de impacto detallado"""
        # Conversión de energía a megatones TNT
        energy_mt = kinetic_energy / (4.184e15)  # 1 megatón = 4.184e15 Joules
        
        # Estimación del diámetro del cráter (fórmula simplificada)
        crater_diameter = props.diameter_m * 20  # Factor simplificado
        
        # Radio de daño estimado
        damage_radius = crater_diameter * 10  # Factor simplificado
        
        # Área de impacto
        impact_area = math.pi * (damage_radius/1000)**2  # En km²
        
        return ImpactAnalysis(
            kinetic_energy_j=kinetic_energy,
            impact_energy_mt=energy_mt,
            crater_diameter_km=crater_diameter/1000,
            damage_radius_km=damage_radius/1000,
            impact_area_km2=impact_area
        )
    
    def _evaluate_risk_factors(self, props: PhysicalProperties) -> RiskFactors:
        """Evalúa factores de riesgo del asteroide"""
        # Factor de tamaño (mayor tamaño = mayor riesgo)
        size_factor = min(props.diameter_m / 1000, 1.0)  # Normalizado
        
        # Factor de velocidad (mayor velocidad = mayor riesgo)
        velocity_factor = min(props.velocity_km_s / 50, 1.0)  # Normalizado
        
        # Factor de densidad (mayor densidad = mayor riesgo)
        density_factor = min(props.density_kg_m3 / 8000, 1.0)  # Normalizado
        
        return RiskFactors(
            size_factor=size_factor,
            velocity_factor=velocity_factor,
            density_factor=density_factor,
            composition_uncertainty=0.3,  # Valor por defecto
            orbital_uncertainty=0.2  # Valor por defecto
        )
    
    def _assess_risk(self, risk_factors: RiskFactors, impact_analysis: ImpactAnalysis) -> RiskAssessment:
        """Evalúa el riesgo general del asteroide"""
        # Cálculo simplificado del riesgo
        risk_score = (
            risk_factors.size_factor * 0.4 +
            risk_factors.velocity_factor * 0.3 +
            risk_factors.density_factor * 0.2 +
            risk_factors.composition_uncertainty * 0.1
        )
        
        # Determinar nivel de riesgo
        if risk_score < 0.2:
            risk_level = "Muy Bajo"
        elif risk_score < 0.4:
            risk_level = "Bajo"
        elif risk_score < 0.6:
            risk_level = "Moderado"
        elif risk_score < 0.8:
            risk_level = "Alto"
        else:
            risk_level = "Crítico"
        
        return RiskAssessment(
            overall_risk_score=risk_score,
            risk_level=risk_level,
            primary_concerns=self._identify_primary_concerns(risk_factors),
            mitigation_priority=self._calculate_mitigation_priority(risk_score)
        )
    
    def _assess_data_quality(self, props: PhysicalProperties) -> DataQuality:
        """Evalúa la calidad de los datos de entrada"""
        # Verificar completitud de datos
        completeness = 1.0 if all([
            props.diameter_m > 0,
            props.velocity_km_s > 0,
            props.mass_kg > 0,
            props.density_kg_m3 > 0
        ]) else 0.8
        
        # Verificar rangos razonables
        reasonableness = 1.0
        if props.diameter_m > 10000 or props.diameter_m < 1:
            reasonableness -= 0.2
        if props.velocity_km_s > 100 or props.velocity_km_s < 1:
            reasonableness -= 0.2
        
        return DataQuality(
            completeness_score=completeness,
            accuracy_score=reasonableness,
            consistency_score=0.9,  # Valor por defecto
            reliability_score=min(completeness, reasonableness)
        )
    
    def _assess_neo_data_quality(self, neo_data: Dict[str, Any]) -> DataQuality:
        """Evalúa la calidad de datos de un NEO específico"""
        completeness = 1.0
        if not neo_data.get("diameter_min_m") or not neo_data.get("diameter_max_m"):
            completeness -= 0.3
        if not neo_data.get("velocity_km_s"):
            completeness -= 0.2
        
        return DataQuality(
            completeness_score=completeness,
            accuracy_score=0.8,  # Valor por defecto
            consistency_score=0.9,
            reliability_score=completeness * 0.8
        )
    
    def _calculate_prediction_reliability(self, neo_data: Dict[str, Any]) -> PredictionReliability:
        """Calcula la confiabilidad de las predicciones"""
        return PredictionReliability(
            model_confidence=0.85,  # Valor por defecto
            data_freshness=0.9,
            prediction_stability=0.8,
            uncertainty_quantification=0.7
        )
    
    def _calculate_confidence_score(self, data_quality: DataQuality, risk_factors: RiskFactors) -> float:
        """Calcula el puntaje de confianza general"""
        return (data_quality.reliability_score + 
                (1 - risk_factors.composition_uncertainty) + 
                (1 - risk_factors.orbital_uncertainty)) / 3
    
    def _calculate_overall_confidence(self, data_quality: DataQuality, prediction_reliability: PredictionReliability) -> float:
        """Calcula la confianza general"""
        return (data_quality.reliability_score + prediction_reliability.model_confidence) / 2
    
    def _generate_recommendations(self, data_quality: DataQuality, prediction_reliability: PredictionReliability) -> list:
        """Genera recomendaciones basadas en la calidad de datos"""
        recommendations = []
        
        if data_quality.completeness_score < 0.8:
            recommendations.append("Mejorar completitud de datos de entrada")
        
        if prediction_reliability.model_confidence < 0.8:
            recommendations.append("Actualizar modelos de predicción")
        
        if not recommendations:
            recommendations.append("Datos de alta calidad - análisis confiable")
        
        return recommendations
    
    def _calculate_impact_probability(self, props: PhysicalProperties) -> float:
        """Calcula probabilidad de impacto (simplificada)"""
        # Modelo simplificado basado en tamaño y velocidad
        base_probability = 0.001  # Probabilidad base muy baja
        
        # Ajustar por tamaño (asteroides más grandes son más fáciles de detectar)
        size_factor = min(props.diameter_m / 100, 1.0)
        
        # Ajustar por velocidad (velocidades extremas son más peligrosas)
        velocity_factor = min(props.velocity_km_s / 30, 1.0)
        
        return base_probability * (1 + size_factor + velocity_factor)
    
    def _determine_risk_category(self, impact_analysis: ImpactAnalysis, probability: float) -> str:
        """Determina la categoría de riesgo"""
        if impact_analysis.impact_energy_mt > 1000 and probability > 0.01:
            return "Crítico"
        elif impact_analysis.impact_energy_mt > 100 and probability > 0.001:
            return "Alto"
        elif impact_analysis.impact_energy_mt > 10 and probability > 0.0001:
            return "Moderado"
        elif impact_analysis.impact_energy_mt > 1:
            return "Bajo"
        else:
            return "Muy Bajo"
    
    def _calculate_prediction_confidence(self, props: PhysicalProperties) -> float:
        """Calcula el nivel de confianza de la predicción"""
        # Basado en la calidad de los datos de entrada
        confidence = 0.8  # Base
        
        if props.diameter_m > 0 and props.velocity_km_s > 0:
            confidence += 0.1
        
        if props.mass_kg > 0 and props.density_kg_m3 > 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _create_hybrid_summary(self, results: Dict[str, Any], request: HybridAnalysisRequest) -> HybridAnalysisSummary:
        """Crea un resumen del análisis híbrido"""
        return HybridAnalysisSummary(
            analysis_type=request.analysis_type,
            components_analyzed=list(results.keys()),
            overall_confidence=self._calculate_hybrid_confidence(results),
            key_findings=self._extract_key_findings(results),
            risk_assessment=self._assess_hybrid_risk(results)
        )
    
    def _calculate_hybrid_confidence(self, results: Dict[str, Any]) -> float:
        """Calcula la confianza del análisis híbrido"""
        if not results:
            return 0.0
        
        confidences = []
        for result in results.values():
            if hasattr(result, 'confidence_score'):
                confidences.append(result.confidence_score)
            elif hasattr(result, 'overall_confidence'):
                confidences.append(result.overall_confidence)
        
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    def _extract_key_findings(self, results: Dict[str, Any]) -> list:
        """Extrae hallazgos clave del análisis"""
        findings = []
        
        for component, result in results.items():
            if hasattr(result, 'risk_assessment'):
                findings.append(f"Riesgo {component}: {result.risk_assessment.risk_level}")
            elif hasattr(result, 'risk_category'):
                findings.append(f"Categoría de riesgo: {result.risk_category}")
        
        return findings if findings else ["Análisis completado exitosamente"]
    
    def _assess_hybrid_risk(self, results: Dict[str, Any]) -> str:
        """Evalúa el riesgo general del análisis híbrido"""
        risk_levels = []
        
        for result in results.values():
            if hasattr(result, 'risk_assessment'):
                risk_levels.append(result.risk_assessment.risk_level)
            elif hasattr(result, 'risk_category'):
                risk_levels.append(result.risk_category)
        
        if not risk_levels:
            return "Desconocido"
        
        # Retornar el nivel de riesgo más alto encontrado
        risk_priority = ["Crítico", "Alto", "Moderado", "Bajo", "Muy Bajo"]
        for risk in risk_priority:
            if risk in risk_levels:
                return risk
        
        return "Moderado"
    
    def _generate_hybrid_recommendations(self, results: Dict[str, Any]) -> list:
        """Genera recomendaciones basadas en el análisis híbrido"""
        recommendations = []
        
        for component, result in results.items():
            if hasattr(result, 'recommendations'):
                recommendations.extend(result.recommendations)
        
        if not recommendations:
            recommendations.append("Continuar monitoreo regular")
        
        return list(set(recommendations))  # Eliminar duplicados
    
    def _identify_primary_concerns(self, risk_factors: RiskFactors) -> list:
        """Identifica las principales preocupaciones"""
        concerns = []
        
        if risk_factors.size_factor > 0.7:
            concerns.append("Tamaño significativo")
        if risk_factors.velocity_factor > 0.7:
            concerns.append("Alta velocidad")
        if risk_factors.composition_uncertainty > 0.5:
            concerns.append("Composición incierta")
        
        return concerns if concerns else ["Riesgo bajo"]
    
    def _calculate_mitigation_priority(self, risk_score: float) -> str:
        """Calcula la prioridad de mitigación"""
        if risk_score > 0.8:
            return "Crítica"
        elif risk_score > 0.6:
            return "Alta"
        elif risk_score > 0.4:
            return "Media"
        elif risk_score > 0.2:
            return "Baja"
        else:
            return "Mínima"