"""
ExplainerAgent - Agente que genera explicaciones científicas comprensibles
Traduce datos técnicos complejos a lenguaje natural para usuarios
"""

from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent, AgentState
from ..supervisors.hybrid_supervisor import HybridSupervisor


class ExplainerAgent(BaseAgent):
    """
    Agente que genera explicaciones científicas comprensibles
    
    Responsabilidades:
    - Traducir métricas técnicas a lenguaje natural
    - Generar explicaciones de riesgo en términos comprensibles
    - Crear narrativas sobre predicciones y análisis
    - Proporcionar contexto científico para decisiones
    """
    
    def __init__(self, supervisor: Optional[HybridSupervisor] = None):
        super().__init__(
            name="ExplainerAgent",
            description="Genera explicaciones científicas comprensibles de datos de asteroides"
        )
        self.supervisor = supervisor
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Ejecuta la generación de explicaciones científicas
        
        Args:
            state: Estado actual del agente con datos de asteroides
            
        Returns:
            Estado actualizado con explicaciones generadas
        """
        print("📚 ExplainerAgent: Generando explicaciones científicas...")
        
        try:
            if not self.validate_input(state):
                self.log_error(state, "Datos de entrada inválidos para explicación")
                return state
            
            # Obtener datos del estado
            asteroid_data = state.data_collection_result.get("asteroid_data", {})
            trajectory_analysis = state.trajectory_analysis
            impact_analysis = state.impact_analysis
            mitigation_analysis = state.mitigation_analysis
            
            # Generar explicaciones
            explanations = {}
            
            # 1. Explicación general del asteroide
            if asteroid_data:
                explanations["asteroid_summary"] = self._explain_asteroid_basics(asteroid_data)
            
            # 2. Explicación de trayectoria
            if trajectory_analysis:
                explanations["trajectory_explanation"] = self._explain_trajectory(trajectory_analysis)
            
            # 3. Explicación de impacto
            if impact_analysis:
                explanations["impact_explanation"] = self._explain_impact(impact_analysis)
            
            # 4. Explicación de mitigación
            if mitigation_analysis:
                explanations["mitigation_explanation"] = self._explain_mitigation(mitigation_analysis)
            
            # 5. Explicación de riesgo general
            explanations["risk_summary"] = self._explain_risk_overview(
                asteroid_data, trajectory_analysis, impact_analysis
            )
            
            # Actualizar estado
            state.explanation_data = {
                "results": explanations,
                "status": "success",
                "message": "Explicaciones generadas exitosamente"
            }
            
            print("✅ ExplainerAgent: Explicaciones generadas exitosamente")
            
        except Exception as e:
            self.log_error(state, f"Error generando explicaciones: {str(e)}")
        
        return state
    
    def _explain_asteroid_basics(self, asteroid_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera explicación básica del asteroide"""
        try:
            name = asteroid_data.get('name', 'Asteroid desconocido')
            diameter = asteroid_data.get('diameter', 0)
            is_potentially_hazardous = asteroid_data.get('is_potentially_hazardous', False)
            
            # Convertir diámetro a metros si está en kilómetros
            if diameter > 1000:  # Asumir que está en metros
                diameter_km = diameter / 1000
            else:
                diameter_km = diameter
            
            # Generar explicación del tamaño
            size_explanation = self._explain_size(diameter_km)
            
            # Generar explicación del peligro
            hazard_explanation = self._explain_hazard_status(is_potentially_hazardous)
            
            # Generar contexto científico
            scientific_context = self._generate_scientific_context(diameter_km, is_potentially_hazardous)
            
            # Crear resumen general
            summary = f"El asteroide {name} es un objeto espacial de {diameter_km:.1f} km de diámetro. {size_explanation} {hazard_explanation}"
            
            return {
                "summary": summary,
                "key_facts": [
                    f"Nombre: {name}",
                    f"Diámetro: {diameter_km:.1f} km",
                    f"Estado de peligro: {'Potencialmente peligroso' if is_potentially_hazardous else 'No peligroso'}",
                    f"Clasificación: {self._classify_asteroid_size(diameter_km)}"
                ],
                "scientific_context": scientific_context,
                "size_category": self._classify_asteroid_size(diameter_km),
                "hazard_level": "Alto" if is_potentially_hazardous else "Bajo"
            }
            
        except Exception as e:
            return {
                "summary": f"Error generando explicación básica: {str(e)}",
                "key_facts": [],
                "scientific_context": "No disponible"
            }
    
    def _explain_size(self, diameter_km: float) -> str:
        """Explica el tamaño del asteroide en términos comprensibles"""
        if diameter_km < 0.1:
            return "Es un asteroide muy pequeño, similar al tamaño de una casa."
        elif diameter_km < 1:
            return "Es un asteroide pequeño, comparable al tamaño de un estadio de fútbol."
        elif diameter_km < 10:
            return "Es un asteroide mediano, similar al tamaño de una ciudad pequeña."
        elif diameter_km < 100:
            return "Es un asteroide grande, comparable al tamaño de una metrópolis."
        else:
            return "Es un asteroide muy grande, similar al tamaño de un país pequeño."
    
    def _explain_hazard_status(self, is_potentially_hazardous: bool) -> str:
        """Explica el estado de peligro del asteroide"""
        if is_potentially_hazardous:
            return "Está clasificado como potencialmente peligroso debido a su tamaño y proximidad a la Tierra."
        else:
            return "No está clasificado como peligroso para la Tierra en este momento."
    
    def _classify_asteroid_size(self, diameter_km: float) -> str:
        """Clasifica el asteroide por tamaño"""
        if diameter_km < 0.1:
            return "Meteoroide"
        elif diameter_km < 1:
            return "Asteroide pequeño"
        elif diameter_km < 10:
            return "Asteroide mediano"
        elif diameter_km < 100:
            return "Asteroide grande"
        else:
            return "Asteroide gigante"
    
    def _generate_scientific_context(self, diameter_km: float, is_potentially_hazardous: bool) -> str:
        """Genera contexto científico sobre el asteroide"""
        context_parts = []
        
        # Contexto sobre el tamaño
        if diameter_km < 1:
            context_parts.append("Los asteroides de este tamaño se queman completamente al entrar en la atmósfera terrestre.")
        elif diameter_km < 10:
            context_parts.append("Asteroides de este tamaño pueden causar daños locales significativos si impactan la Tierra.")
        else:
            context_parts.append("Asteroides de este tamaño pueden causar daños globales catastróficos si impactan la Tierra.")
        
        # Contexto sobre el peligro
        if is_potentially_hazardous:
            context_parts.append("Su clasificación como potencialmente peligroso significa que merece monitoreo continuo.")
        else:
            context_parts.append("Su órbita actual no representa una amenaza inmediata para la Tierra.")
        
        return " ".join(context_parts)
    
    def _explain_trajectory(self, trajectory_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Genera explicación de la trayectoria orbital"""
        try:
            # Extraer datos del análisis de trayectoria
            orbital_period = trajectory_analysis.get('orbital_period_days', 0)
            semi_major_axis = trajectory_analysis.get('semi_major_axis_au', 0)
            eccentricity = trajectory_analysis.get('eccentricity', 0)
            inclination = trajectory_analysis.get('inclination_deg', 0)
            closest_approach = trajectory_analysis.get('closest_approach', {})
            velocity = trajectory_analysis.get('velocity_km_s', 0)
            
            # Generar explicaciones
            orbital_type = self._classify_orbital_type(semi_major_axis, eccentricity)
            period_explanation = self._explain_orbital_period(orbital_period)
            shape_explanation = self._explain_orbital_shape(eccentricity)
            inclination_explanation = self._explain_orbital_inclination(inclination)
            approach_explanation = self._explain_closest_approach(closest_approach)
            velocity_explanation = self._explain_velocity(velocity)
            
            # Crear resumen general
            summary = f"Este asteroide tiene una órbita {orbital_type} con un período de {orbital_period:.0f} días. {period_explanation} {shape_explanation}"
            
            # Generar predicciones futuras
            future_predictions = self._generate_future_predictions(trajectory_analysis)
            
            return {
                "summary": summary,
                "orbital_characteristics": {
                    "orbital_type": orbital_type,
                    "period_explanation": period_explanation,
                    "shape_explanation": shape_explanation,
                    "inclination_explanation": inclination_explanation,
                    "velocity_explanation": velocity_explanation
                },
                "future_predictions": future_predictions,
                "approach_analysis": approach_explanation,
                "orbital_data": {
                    "period_days": orbital_period,
                    "semi_major_axis_au": semi_major_axis,
                    "eccentricity": eccentricity,
                    "inclination_deg": inclination,
                    "velocity_km_s": velocity
                },
                "risk_assessment": self._assess_orbital_risk(trajectory_analysis)
            }
            
        except Exception as e:
            return {
                "summary": f"Error generando explicación de trayectoria: {str(e)}",
                "orbital_characteristics": "No disponible",
                "future_predictions": "No disponible"
            }
    
    def _classify_orbital_type(self, semi_major_axis: float, eccentricity: float) -> str:
        """Clasifica el tipo de órbita"""
        if semi_major_axis < 1.3:
            return "cercana a la Tierra (NEA)"
        elif semi_major_axis < 2.0:
            return "del cinturón interior"
        elif semi_major_axis < 3.5:
            return "del cinturón principal"
        else:
            return "exterior"
    
    def _explain_orbital_period(self, period_days: float) -> str:
        """Explica el período orbital"""
        if period_days < 100:
            return "Completa una órbita alrededor del Sol en menos de 4 meses, muy rápido comparado con la Tierra."
        elif period_days < 400:
            return "Completa una órbita alrededor del Sol en aproximadamente un año, similar a la Tierra."
        elif period_days < 1000:
            return "Completa una órbita alrededor del Sol en varios años, más lenta que la Tierra."
        else:
            return "Completa una órbita alrededor del Sol en décadas, mucho más lenta que la Tierra."
    
    def _explain_orbital_shape(self, eccentricity: float) -> str:
        """Explica la forma de la órbita"""
        if eccentricity < 0.1:
            return "Tiene una órbita casi circular, muy estable."
        elif eccentricity < 0.3:
            return "Tiene una órbita ligeramente elíptica, con variaciones moderadas en la distancia al Sol."
        elif eccentricity < 0.7:
            return "Tiene una órbita bastante elíptica, con grandes variaciones en la distancia al Sol."
        else:
            return "Tiene una órbita muy elíptica, con variaciones extremas en la distancia al Sol."
    
    def _explain_orbital_inclination(self, inclination: float) -> str:
        """Explica la inclinación orbital"""
        if inclination < 5:
            return "Su órbita está casi en el mismo plano que los planetas, muy estable."
        elif inclination < 15:
            return "Su órbita está ligeramente inclinada respecto al plano planetario."
        elif inclination < 30:
            return "Su órbita está moderadamente inclinada, cruzando el plano planetario regularmente."
        else:
            return "Su órbita está muy inclinada, con trayectorias impredecibles respecto a los planetas."
    
    def _explain_closest_approach(self, closest_approach: Dict[str, Any]) -> Dict[str, Any]:
        """Explica la aproximación más cercana"""
        if not closest_approach:
            return {"summary": "No hay datos de aproximación cercana disponibles"}
        
        distance_km = float(closest_approach.get('distance_km', 0))
        date = closest_approach.get('date', 'desconocida')
        velocity = closest_approach.get('velocity_km_s', 0)
        
        # Convertir distancia a unidades comprensibles
        if distance_km < 1000:
            distance_explanation = f"muy cercana ({distance_km:.0f} km)"
        elif distance_km < 10000:
            distance_explanation = f"cercana ({distance_km/1000:.1f} mil km)"
        elif distance_km < 100000:
            distance_explanation = f"moderada ({distance_km/1000:.0f} mil km)"
        else:
            distance_explanation = f"lejana ({distance_km/1000:.0f} mil km)"
        
        return {
            "summary": f"Su aproximación más cercana será el {date} a una distancia {distance_explanation}",
            "distance_km": distance_km,
            "date": date,
            "velocity_km_s": velocity,
            "risk_level": self._assess_approach_risk(distance_km)
        }
    
    def _explain_velocity(self, velocity_km_s: float) -> str:
        """Explica la velocidad orbital"""
        if velocity_km_s < 20:
            return f"Se mueve a {velocity_km_s:.1f} km/s, relativamente lento para un asteroide."
        elif velocity_km_s < 40:
            return f"Se mueve a {velocity_km_s:.1f} km/s, velocidad típica de asteroides."
        elif velocity_km_s < 60:
            return f"Se mueve a {velocity_km_s:.1f} km/s, bastante rápido para un asteroide."
        else:
            return f"Se mueve a {velocity_km_s:.1f} km/s, muy rápido, posiblemente un cometa o objeto interestelar."
    
    def _generate_future_predictions(self, trajectory_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Genera predicciones futuras basadas en la trayectoria"""
        confidence = trajectory_analysis.get('confidence_metrics', {}).get('orbital_confidence', 0.5)
        
        predictions = {
            "short_term": "En los próximos 10 años, la órbita se mantendrá relativamente estable.",
            "medium_term": "En las próximas décadas, pueden ocurrir aproximaciones cercanas ocasionales.",
            "long_term": "En siglos futuros, la órbita puede evolucionar debido a perturbaciones gravitacionales.",
            "confidence_level": self._assess_prediction_confidence(confidence)
        }
        
        return predictions
    
    def _assess_approach_risk(self, distance_km: float) -> str:
        """Evalúa el riesgo de aproximación cercana"""
        if distance_km < 1000:
            return "Muy alto - Distancia extremadamente cercana"
        elif distance_km < 10000:
            return "Alto - Distancia muy cercana"
        elif distance_km < 100000:
            return "Moderado - Distancia cercana pero segura"
        else:
            return "Bajo - Distancia segura"
    
    def _assess_prediction_confidence(self, confidence: float) -> str:
        """Evalúa la confianza de las predicciones"""
        if confidence > 0.8:
            return "Muy alta - Predicciones muy confiables"
        elif confidence > 0.6:
            return "Alta - Predicciones confiables"
        elif confidence > 0.4:
            return "Moderada - Predicciones con cierta incertidumbre"
        else:
            return "Baja - Predicciones inciertas"
    
    def _assess_orbital_risk(self, trajectory_analysis: Dict[str, Any]) -> str:
        """Evalúa el riesgo general de la órbita"""
        closest_approach = trajectory_analysis.get('closest_approach', {})
        distance_km = float(closest_approach.get('distance_km', float('inf')))
        eccentricity = trajectory_analysis.get('eccentricity', 0)
        
        if distance_km < 10000 and eccentricity > 0.5:
            return "Alto - Órbita inestable con aproximaciones cercanas frecuentes"
        elif distance_km < 100000:
            return "Moderado - Aproximaciones cercanas ocasionales"
        else:
            return "Bajo - Órbita estable y distante"
    
    def _explain_impact(self, impact_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Genera explicación del impacto potencial"""
        try:
            # Extraer datos del análisis de impacto
            impact_energy = impact_analysis.get('impact_energy', {})
            crater_diameter = impact_analysis.get('crater_diameter_km', 0)
            seismic_radius = impact_analysis.get('seismic_radius_km', 0)
            tsunami_radius = impact_analysis.get('tsunami_radius_km', 0)
            thermal_radius = impact_analysis.get('thermal_radius_km', 0)
            blast_radius = impact_analysis.get('blast_radius_km', 0)
            
            # Obtener energía en megatones
            energy_mt = impact_energy.get('megatons', 0) if isinstance(impact_energy, dict) else 0
            
            # Generar explicaciones
            energy_explanation = self._explain_impact_energy(energy_mt)
            crater_explanation = self._explain_crater_effects(crater_diameter)
            seismic_explanation = self._explain_seismic_effects(seismic_radius)
            tsunami_explanation = self._explain_tsunami_effects(tsunami_radius)
            thermal_explanation = self._explain_thermal_effects(thermal_radius)
            blast_explanation = self._explain_blast_effects(blast_radius)
            
            # Crear resumen general
            summary = f"Si este asteroide impactara la Tierra, liberaría {energy_mt:.1f} megatones de energía. {energy_explanation} {crater_explanation}"
            
            # Generar comparaciones históricas
            historical_comparison = self._generate_historical_comparison(energy_mt)
            
            return {
                "summary": summary,
                "energy_comparison": energy_explanation,
                "damage_assessment": {
                    "crater_effects": crater_explanation,
                    "seismic_effects": seismic_explanation,
                    "tsunami_effects": tsunami_explanation,
                    "thermal_effects": thermal_explanation,
                    "blast_effects": blast_explanation
                },
                "historical_comparison": historical_comparison,
                "impact_zones": {
                    "crater_diameter_km": crater_diameter,
                    "seismic_radius_km": seismic_radius,
                    "tsunami_radius_km": tsunami_radius,
                    "thermal_radius_km": thermal_radius,
                    "blast_radius_km": blast_radius
                },
                "severity_level": self._assess_impact_severity(energy_mt)
            }
            
        except Exception as e:
            return {
                "summary": f"Error generando explicación de impacto: {str(e)}",
                "energy_comparison": "No disponible",
                "damage_assessment": "No disponible"
            }
    
    def _explain_impact_energy(self, energy_mt: float) -> str:
        """Explica la energía de impacto en términos comprensibles"""
        if energy_mt < 0.1:
            return "Equivalente a una explosión nuclear pequeña, similar a la bomba de Hiroshima."
        elif energy_mt < 1:
            return "Equivalente a una explosión nuclear mediana, comparable a las pruebas nucleares más grandes."
        elif energy_mt < 10:
            return "Equivalente a múltiples bombas nucleares, causando devastación regional."
        elif energy_mt < 100:
            return "Equivalente a decenas de bombas nucleares, con efectos continentales."
        else:
            return "Equivalente a cientos de bombas nucleares, con efectos globales catastróficos."
    
    def _explain_crater_effects(self, crater_diameter_km: float) -> str:
        """Explica los efectos del cráter"""
        if crater_diameter_km < 1:
            return f"Crearía un cráter de {crater_diameter_km:.1f} km, similar al tamaño de un barrio pequeño."
        elif crater_diameter_km < 10:
            return f"Crearía un cráter de {crater_diameter_km:.1f} km, comparable al tamaño de una ciudad mediana."
        elif crater_diameter_km < 50:
            return f"Crearía un cráter de {crater_diameter_km:.1f} km, similar al tamaño de una metrópolis."
        else:
            return f"Crearía un cráter de {crater_diameter_km:.1f} km, comparable al tamaño de un país pequeño."
    
    def _explain_seismic_effects(self, seismic_radius_km: float) -> str:
        """Explica los efectos sísmicos"""
        if seismic_radius_km < 10:
            return f"Generaría terremotos en un radio de {seismic_radius_km:.1f} km, similares a un terremoto moderado."
        elif seismic_radius_km < 100:
            return f"Generaría terremotos en un radio de {seismic_radius_km:.1f} km, comparables a un terremoto fuerte."
        else:
            return f"Generaría terremotos en un radio de {seismic_radius_km:.1f} km, similares a un terremoto catastrófico."
    
    def _explain_tsunami_effects(self, tsunami_radius_km: float) -> str:
        """Explica los efectos de tsunami"""
        if tsunami_radius_km < 50:
            return f"Generaría tsunamis en un radio de {tsunami_radius_km:.1f} km, afectando costas cercanas."
        elif tsunami_radius_km < 500:
            return f"Generaría tsunamis en un radio de {tsunami_radius_km:.1f} km, afectando múltiples países costeros."
        else:
            return f"Generaría tsunamis en un radio de {tsunami_radius_km:.1f} km, afectando continentes enteros."
    
    def _explain_thermal_effects(self, thermal_radius_km: float) -> str:
        """Explica los efectos térmicos"""
        if thermal_radius_km < 20:
            return f"Causaría quemaduras graves en un radio de {thermal_radius_km:.1f} km."
        elif thermal_radius_km < 100:
            return f"Causaría incendios masivos en un radio de {thermal_radius_km:.1f} km."
        else:
            return f"Causaría incendios continentales en un radio de {thermal_radius_km:.1f} km."
    
    def _explain_blast_effects(self, blast_radius_km: float) -> str:
        """Explica los efectos de la onda expansiva"""
        if blast_radius_km < 10:
            return f"La onda expansiva devastaría un radio de {blast_radius_km:.1f} km."
        elif blast_radius_km < 50:
            return f"La onda expansiva devastaría un radio de {blast_radius_km:.1f} km, destruyendo ciudades enteras."
        else:
            return f"La onda expansiva devastaría un radio de {blast_radius_km:.1f} km, destruyendo regiones completas."
    
    def _generate_historical_comparison(self, energy_mt: float) -> str:
        """Genera comparación con eventos históricos"""
        if energy_mt < 0.02:
            return "Similar a la explosión de Tunguska en 1908 (15 megatones)."
        elif energy_mt < 0.1:
            return "Similar a la bomba de Hiroshima (15 kilotones) multiplicada por 1000."
        elif energy_mt < 1:
            return "Similar a la bomba de Tsar Bomba, la más grande jamás detonada (50 megatones)."
        elif energy_mt < 10:
            return "Similar al impacto de Chicxulub que extinguió a los dinosaurios (100 millones de megatones)."
        else:
            return "Similar a los impactos más catastróficos de la historia de la Tierra."
    
    def _assess_impact_severity(self, energy_mt: float) -> str:
        """Evalúa la severidad del impacto"""
        if energy_mt < 0.1:
            return "Local - Daños limitados a un área pequeña"
        elif energy_mt < 1:
            return "Regional - Daños en una región o país"
        elif energy_mt < 10:
            return "Continental - Daños en un continente"
        elif energy_mt < 100:
            return "Global - Efectos en todo el planeta"
        else:
            return "Extinción - Efectos catastróficos globales"
    
    def _explain_mitigation(self, mitigation_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Genera explicación de estrategias de mitigación"""
        try:
            strategies = mitigation_analysis.get('strategies', [])
            priority = mitigation_analysis.get('priority', 'Media')
            confidence = mitigation_analysis.get('confidence', 0.5)
            
            # Analizar estrategias factibles
            feasible_strategies = []
            for strategy in strategies:
                if strategy.get('feasibility') in ['Alta', 'Media']:
                    feasible_strategies.append(f"{strategy['name']} ({strategy['feasibility']})")
            
            if not feasible_strategies:
                feasible_strategies = ["Ninguna estrategia factible identificada"]
            
            # Generar análisis costo-beneficio
            total_cost = sum(strategy.get('cost', 0) for strategy in strategies)
            cost_benefit = self._analyze_cost_benefit(total_cost, priority, confidence)
            
            # Calcular probabilidad de éxito
            success_probability = self._calculate_success_probability(strategies, confidence)
            
            # Generar timeline de implementación
            timeline = self._generate_implementation_timeline(priority, strategies)
            
            # Crear resumen
            summary = f"Se identificaron {len(feasible_strategies)} estrategias factibles para mitigar el riesgo. "
            summary += f"La prioridad es {priority.lower()} con una confianza del {confidence*100:.0f}%. "
            summary += f"El costo estimado es de ${total_cost:,.0f} y la probabilidad de éxito es del {success_probability*100:.0f}%."
            
            return {
                "summary": summary,
                "feasible_strategies": feasible_strategies,
                "cost_benefit": cost_benefit,
                "implementation_timeline": timeline,
                "success_probability": f"{success_probability*100:.0f}%"
            }
            
        except Exception as e:
            return {
                "summary": f"Error generando explicación de mitigación: {str(e)}",
                "feasible_strategies": ["Error en análisis"],
                "cost_benefit": "No disponible",
                "implementation_timeline": "No disponible",
                "success_probability": "0%"
            }
    
    def _analyze_cost_benefit(self, total_cost: float, priority: str, confidence: float) -> str:
        """Analiza la relación costo-beneficio"""
        if total_cost < 1000000000:  # < 1B
            cost_level = "bajo"
        elif total_cost < 10000000000:  # < 10B
            cost_level = "moderado"
        else:
            cost_level = "alto"
        
        if priority == "Alta":
            benefit_level = "muy alto"
        elif priority == "Media":
            benefit_level = "moderado"
        else:
            benefit_level = "bajo"
        
        return f"Costo {cost_level} (${total_cost:,.0f}) con beneficio {benefit_level} para la defensa planetaria. Confianza: {confidence*100:.0f}%"
    
    def _calculate_success_probability(self, strategies: List[Dict], confidence: float) -> float:
        """Calcula la probabilidad de éxito de las estrategias"""
        if not strategies:
            return 0.0
        
        # Calcular probabilidad basada en factibilidad y confianza
        feasibility_scores = []
        for strategy in strategies:
            feasibility = strategy.get('feasibility', 'Baja')
            if feasibility == 'Alta':
                feasibility_scores.append(0.8)
            elif feasibility == 'Media':
                feasibility_scores.append(0.6)
            else:
                feasibility_scores.append(0.3)
        
        avg_feasibility = sum(feasibility_scores) / len(feasibility_scores)
        return min(0.95, avg_feasibility * confidence)
    
    def _generate_implementation_timeline(self, priority: str, strategies: List[Dict]) -> str:
        """Genera timeline de implementación"""
        if priority == "Alta":
            timeline = "5-10 años"
        elif priority == "Media":
            timeline = "10-20 años"
        else:
            timeline = "20+ años"
        
        if strategies:
            timeline += f" para {len(strategies)} estrategias identificadas"
        
        return timeline
    
    def _explain_risk_overview(self, asteroid_data: Dict[str, Any], 
                              trajectory_analysis: Dict[str, Any], 
                              impact_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Genera resumen general del riesgo"""
        try:
            # Analizar datos del asteroide
            diameter = asteroid_data.get('diameter', 0)
            is_hazardous = asteroid_data.get('is_potentially_hazardous', False)
            
            # Analizar trayectoria
            closest_approach = trajectory_analysis.get('closest_approach', {})
            distance_km = float(closest_approach.get('distance_km', float('inf')))
            eccentricity = trajectory_analysis.get('eccentricity', 0)
            
            # Analizar impacto
            impact_energy = impact_analysis.get('impact_energy', {})
            energy_mt = impact_energy.get('megatons', 0)
            
            # Calcular riesgo general
            overall_risk = self._calculate_overall_risk(diameter, is_hazardous, distance_km, energy_mt)
            
            # Identificar preocupaciones clave
            key_concerns = self._identify_key_concerns(diameter, is_hazardous, distance_km, eccentricity, energy_mt)
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(overall_risk, key_concerns, is_hazardous)
            
            # Determinar prioridad de monitoreo
            monitoring_priority = self._determine_monitoring_priority(overall_risk, key_concerns)
            
            return {
                "overall_risk": overall_risk,
                "key_concerns": key_concerns,
                "recommendations": recommendations,
                "monitoring_priority": monitoring_priority
            }
            
        except Exception as e:
            return {
                "overall_risk": f"Error en análisis: {str(e)}",
                "key_concerns": ["Error en evaluación"],
                "recommendations": ["Verificar datos"],
                "monitoring_priority": "Desconocida"
            }
    
    def _calculate_overall_risk(self, diameter: float, is_hazardous: bool, distance_km: float, energy_mt: float) -> str:
        """Calcula el riesgo general del asteroide"""
        risk_factors = 0
        
        # Factor de tamaño
        if diameter > 1000:  # > 1km
            risk_factors += 3
        elif diameter > 100:  # > 100m
            risk_factors += 2
        elif diameter > 10:  # > 10m
            risk_factors += 1
        
        # Factor de peligrosidad
        if is_hazardous:
            risk_factors += 2
        
        # Factor de distancia
        if distance_km < 10000:  # < 10,000 km
            risk_factors += 3
        elif distance_km < 100000:  # < 100,000 km
            risk_factors += 2
        elif distance_km < 1000000:  # < 1,000,000 km
            risk_factors += 1
        
        # Factor de energía de impacto
        if energy_mt > 100:  # > 100 megatones
            risk_factors += 3
        elif energy_mt > 10:  # > 10 megatones
            risk_factors += 2
        elif energy_mt > 1:  # > 1 megatón
            risk_factors += 1
        
        # Clasificar riesgo
        if risk_factors >= 8:
            return "Muy Alto - Requiere acción inmediata"
        elif risk_factors >= 6:
            return "Alto - Monitoreo intensivo necesario"
        elif risk_factors >= 4:
            return "Moderado - Monitoreo regular recomendado"
        elif risk_factors >= 2:
            return "Bajo - Monitoreo rutinario suficiente"
        else:
            return "Muy Bajo - Monitoreo básico"
    
    def _identify_key_concerns(self, diameter: float, is_hazardous: bool, distance_km: float, 
                              eccentricity: float, energy_mt: float) -> List[str]:
        """Identifica las preocupaciones clave"""
        concerns = []
        
        if diameter > 1000:
            concerns.append("Asteroides de gran tamaño pueden causar daños globales")
        
        if is_hazardous:
            concerns.append("Clasificado como potencialmente peligroso por la NASA")
        
        if distance_km < 10000:
            concerns.append("Aproximaciones extremadamente cercanas detectadas")
        elif distance_km < 100000:
            concerns.append("Aproximaciones cercanas que requieren monitoreo")
        
        if eccentricity > 0.5:
            concerns.append("Órbita altamente excéntrica e impredecible")
        
        if energy_mt > 100:
            concerns.append("Energía de impacto suficiente para causar devastación regional")
        elif energy_mt > 10:
            concerns.append("Energía de impacto significativa que requiere evaluación")
        
        if not concerns:
            concerns.append("No se identificaron preocupaciones significativas")
        
        return concerns
    
    def _generate_recommendations(self, overall_risk: str, key_concerns: List[str], is_hazardous: bool) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        recommendations = []
        
        if "Muy Alto" in overall_risk or "Alto" in overall_risk:
            recommendations.append("Iniciar análisis de misión de mitigación inmediatamente")
            recommendations.append("Coordinar con agencias espaciales internacionales")
            recommendations.append("Preparar sistemas de alerta temprana")
        
        if "Moderado" in overall_risk:
            recommendations.append("Aumentar frecuencia de observaciones")
            recommendations.append("Refinar modelos de predicción orbital")
            recommendations.append("Evaluar opciones de mitigación preventiva")
        
        if is_hazardous:
            recommendations.append("Incluir en lista de prioridades de monitoreo")
            recommendations.append("Actualizar modelos de riesgo regularmente")
        
        if "Aproximaciones extremadamente cercanas" in key_concerns:
            recommendations.append("Implementar monitoreo continuo 24/7")
            recommendations.append("Preparar protocolos de emergencia")
        
        if not recommendations:
            recommendations.append("Continuar monitoreo rutinario")
            recommendations.append("Revisar en próximos 6 meses")
        
        return recommendations
    
    def _determine_monitoring_priority(self, overall_risk: str, key_concerns: List[str]) -> str:
        """Determina la prioridad de monitoreo"""
        if "Muy Alto" in overall_risk:
            return "Crítica - Monitoreo continuo"
        elif "Alto" in overall_risk:
            return "Alta - Monitoreo diario"
        elif "Moderado" in overall_risk:
            return "Media - Monitoreo semanal"
        elif "Bajo" in overall_risk:
            return "Baja - Monitoreo mensual"
        else:
            return "Mínima - Monitoreo trimestral"
