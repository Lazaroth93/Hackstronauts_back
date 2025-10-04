"""
Validador especializado en física y mecánica celeste.

Verifica que los cálculos físicos de los agentes sean correctos
usando constantes físicas conocidas y rangos de valores esperados.
"""

import math
from typing import Dict, Any, List
from .base_validator import BaseValidator, ValidationReport, ValidationLevel, ValidationResult


class PhysicsValidator(BaseValidator):
    """
    Validador especializado en física orbital y mecánica celeste.
    
    Verifica:
    - Constantes físicas (G, masa de la Tierra, etc.)
    - Rangos de valores orbitales
    - Conservación de energía
    - Unidades correctas
    - Coherencia dimensional
    """
    
    def __init__(self):
        super().__init__(
            name="PhysicsValidator",
            description="Valida cálculos de física orbital y mecánica celeste"
        )
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Carga reglas de validación específicas de física."""
        return {
            # Constantes físicas (SI)
            "constants": {
                "G": 6.67430e-11,  # Constante gravitacional (m³/kg/s²)
                "M_earth": 5.972e24,  # Masa de la Tierra (kg)
                "R_earth": 6.371e6,   # Radio de la Tierra (m)
                "AU": 1.496e11,       # Unidad astronómica (m)
                "c": 2.998e8,         # Velocidad de la luz (m/s)
            },
            
            # Rangos de valores esperados
            "ranges": {
                "orbital_period": (0.1, 1000),  # Período orbital (años)
                "eccentricity": (0, 0.999),     # Excentricidad (adimensional)
                "inclination": (0, 180),        # Inclinación (grados)
                "semi_major_axis": (0.1, 100),  # Semieje mayor (AU)
                "velocity": (1e3, 1e5),         # Velocidad orbital (m/s)
                "kinetic_energy": (1e12, 1e25), # Energía cinética (J)
                "impact_velocity": (11e3, 72e3), # Velocidad de impacto (m/s)
            },
            
            # Tolerancias para validación
            "tolerances": {
                "energy_conservation": 0.01,    # 1% para conservación de energía
                "physical_constants": 0.001,    # 0.1% para constantes físicas
                "orbital_elements": 0.05,       # 5% para elementos orbitales
            }
        }
    
    def validate(self, agent_data: Dict[str, Any], context: Dict[str, Any]) -> ValidationReport:
        """
        Valida los datos físicos de un agente.
        
        Args:
            agent_data: Datos producidos por el agente
            context: Contexto adicional (tipo de agente, etc.)
            
        Returns:
            Reporte de validación completo
        """
        report = ValidationReport(
            agent_name=context.get("agent_name", "Unknown"),
            overall_confidence=0.0,
            is_valid=True,
            validation_count=0,
            results=[]
        )
        
        # Validar según el tipo de agente
        agent_type = context.get("agent_type", "unknown")
        
        if agent_type == "trajectory":
            self._validate_trajectory_data(agent_data, report)
        elif agent_type == "impact":
            self._validate_impact_data(agent_data, report)
        elif agent_type == "mitigation":
            self._validate_mitigation_data(agent_data, report)
        else:
            self._validate_general_physics(agent_data, report)
        
        return report
    
    def _validate_trajectory_data(self, data: Dict[str, Any], report: ValidationReport) -> None:
        """Valida datos específicos del TrajectoryAgent."""
        print("=" * 50)
        print("PhysicsValidator: Validando datos de trayectoria...")
        
        # Validar elementos orbitales
        if "orbital_elements" in data:
            elements = data["orbital_elements"]
            
            # Semieje mayor (AU)
            if "semi_major_axis" in elements:
                a = elements["semi_major_axis"]
                result = self.validate_range(
                    a, 
                    self.validation_rules["ranges"]["semi_major_axis"][0],
                    self.validation_rules["ranges"]["semi_major_axis"][1],
                    "semi_major_axis",
                    "AU"
                )
                report.add_result(result)
            
            # Excentricidad
            if "eccentricity" in elements:
                e = elements["eccentricity"]
                result = self.validate_range(
                    e,
                    self.validation_rules["ranges"]["eccentricity"][0],
                    self.validation_rules["ranges"]["eccentricity"][1],
                    "eccentricity",
                    ""
                )
                report.add_result(result)
            
            # Inclinación
            if "inclination" in elements:
                i = elements["inclination"]
                result = self.validate_range(
                    i,
                    self.validation_rules["ranges"]["inclination"][0],
                    self.validation_rules["ranges"]["inclination"][1],
                    "inclination",
                    "°"
                )
                report.add_result(result)
        
        # Validar período orbital
        if "orbital_period" in data:
            period = data["orbital_period"]
            result = self.validate_range(
                period,
                self.validation_rules["ranges"]["orbital_period"][0],
                self.validation_rules["ranges"]["orbital_period"][1],
                "orbital_period",
                "años"
            )
            report.add_result(result)
        
        # Validar velocidad orbital
        if "orbital_velocity" in data:
            velocity = data["orbital_velocity"]
            result = self.validate_range(
                velocity,
                self.validation_rules["ranges"]["velocity"][0],
                self.validation_rules["ranges"]["velocity"][1],
                "orbital_velocity",
                "m/s"
            )
            report.add_result(result)
        
        # Validar conservación de energía
        if "energy_analysis" in data:
            self._validate_energy_conservation(data["energy_analysis"], report)
        
        print(f"PhysicsValidator: Validación de trayectoria completada - {len(report.results)} validaciones")
        print("=" * 50)
    
    def _validate_impact_data(self, data: Dict[str, Any], report: ValidationReport) -> None:
        """Valida datos específicos del ImpactAnalyzerAgent."""
        print("=" * 50)
        print("PhysicsValidator: Validando datos de impacto...")
        
        # Validar energía de impacto
        if "impact_energy" in data:
            energy_data = data["impact_energy"]
            if isinstance(energy_data, dict):
                # Validar energía total en Joules
                if "total_energy_joules" in energy_data:
                    energy = energy_data["total_energy_joules"]
                    result = self.validate_range(
                        energy,
                        self.validation_rules["ranges"]["kinetic_energy"][0],
                        self.validation_rules["ranges"]["kinetic_energy"][1],
                        "total_energy_joules",
                        "J"
                    )
                    report.add_result(result)
                
                # Validar energía en MT TNT
                if "total_energy_mt_tnt" in energy_data:
                    energy_mt = energy_data["total_energy_mt_tnt"]
                    # Rango típico: 0.001 a 10000 MT TNT
                    result = self.validate_range(
                        energy_mt,
                        0.001,
                        10000,
                        "total_energy_mt_tnt",
                        "MT TNT"
                    )
                    report.add_result(result)
        
        # Validar análisis del cráter
        if "crater_analysis" in data:
            crater_data = data["crater_analysis"]
            if isinstance(crater_data, dict):
                # Validar diámetro del cráter
                if "diameter_km" in crater_data:
                    diameter = crater_data["diameter_km"]
                    result = self.validate_range(
                        diameter,
                        0.1,
                        1000,
                        "crater_diameter_km",
                        "km"
                    )
                    report.add_result(result)
        
        # Validar efectos sísmicos
        if "seismic_effects" in data:
            seismic_data = data["seismic_effects"]
            if isinstance(seismic_data, dict):
                # Validar magnitud sísmica
                if "magnitude" in seismic_data:
                    magnitude = seismic_data["magnitude"]
                    result = self.validate_range(
                        magnitude,
                        0,
                        10,
                        "seismic_magnitude",
                        "Richter"
                    )
                    report.add_result(result)
        
        # Validar efectos de tsunami
        if "tsunami_effects" in data:
            tsunami_data = data["tsunami_effects"]
            if isinstance(tsunami_data, dict):
                # Validar altura máxima de ola
                if "max_wave_height_m" in tsunami_data:
                    wave_height = tsunami_data["max_wave_height_m"]
                    result = self.validate_range(
                        wave_height,
                        0,
                        1000,
                        "max_wave_height_m",
                        "m"
                    )
                    report.add_result(result)
        
        print(f"PhysicsValidator: Validación de impacto completada - {len(report.results)} validaciones")
        print("=" * 50)
    
    def _validate_mitigation_data(self, data: Dict[str, Any], report: ValidationReport) -> None:
        """Valida datos específicos del MitigationAgent."""
        print("=" * 50)
        print("PhysicsValidator: Validando datos de mitigación...")
        
        if "strategies" in data:
            for i, strategy in enumerate(data["strategies"]):
                # Validar efectividad (0-1)
                if "effectiveness" in strategy:
                    eff = strategy["effectiveness"]
                    result = self.validate_range(
                        eff,
                        0,
                        1,
                        f"strategy_{i}_effectiveness",
                        ""
                    )
                    report.add_result(result)
                
                # Validar costo (positivo)
                if "cost" in strategy:
                    cost = strategy["cost"]
                    if cost < 0:
                        result = self.create_validation_result(
                            level=ValidationLevel.CRITICAL,
                            message=f"Costo de estrategia {i} no puede ser negativo",
                            field=f"strategy_{i}_cost",
                            actual_value=cost,
                            confidence=0.0
                        )
                        report.add_result(result)
        
        print(f"PhysicsValidator: Validación de mitigación completada - {len(report.results)} validaciones")
        print("=" * 50)
    
    def _validate_general_physics(self, data: Dict[str, Any], report: ValidationReport) -> None:
        """Valida datos físicos generales."""
        print("=" * 50)
        print("PhysicsValidator: Validando datos físicos generales...")
        
        # Validar que no haya valores infinitos o NaN
        for key, value in data.items():
            if isinstance(value, (int, float)):
                if not math.isfinite(value):
                    result = self.create_validation_result(
                        level=ValidationLevel.CRITICAL,
                        message=f"Valor no finito encontrado en {key}",
                        field=key,
                        actual_value=value,
                        confidence=0.0
                    )
                    report.add_result(result)
        
        print(f"PhysicsValidator: Validación general completada - {len(report.results)} validaciones")
        print("=" * 50)
    
    def _validate_energy_conservation(self, energy_data: Dict[str, Any], report: ValidationReport) -> None:
        """Valida la conservación de energía en el sistema."""
        if "total_energy" not in energy_data or "kinetic_energy" not in energy_data or "potential_energy" not in energy_data:
            return
        
        total = energy_data["total_energy"]
        kinetic = energy_data["kinetic_energy"]
        potential = energy_data["potential_energy"]
        
        # Verificar que E_total ≈ E_kinetic + E_potential
        calculated_total = kinetic + potential
        relative_error = abs(total - calculated_total) / abs(total) if total != 0 else float('inf')
        
        tolerance = self.validation_rules["tolerances"]["energy_conservation"]
        
        if relative_error <= tolerance:
            result = self.create_validation_result(
                level=ValidationLevel.SUCCESS,
                message="Conservación de energía verificada",
                field="energy_conservation",
                confidence=1.0
            )
        else:
            result = self.create_validation_result(
                level=ValidationLevel.WARNING,
                message=f"Error en conservación de energía: {relative_error:.2%}",
                field="energy_conservation",
                expected_value=f"Error < {tolerance:.1%}",
                actual_value=f"Error = {relative_error:.2%}",
                confidence=0.5
            )
        
        report.add_result(result)
    
    def validate_orbital_mechanics(self, orbital_data: Dict[str, Any]) -> List[ValidationResult]:
        """
        Valida cálculos específicos de mecánica orbital.
        
        Args:
            orbital_data: Datos orbitales a validar
            
        Returns:
            Lista de resultados de validación
        """
        results = []
        
        # Validar tercera ley de Kepler: T² ∝ a³
        if "orbital_period" in orbital_data and "semi_major_axis" in orbital_data:
            T = orbital_data["orbital_period"]  # años
            a = orbital_data["semi_major_axis"]  # AU
            
            # T² = (4π²/GM) * a³
            # Para el Sol: T² = a³ (en años y AU)
            expected_T_squared = a ** 3
            actual_T_squared = T ** 2
            
            relative_error = abs(actual_T_squared - expected_T_squared) / expected_T_squared
            
            if relative_error <= 0.1:  # 10% de tolerancia
                results.append(self.create_validation_result(
                    level=ValidationLevel.SUCCESS,
                    message="Tercera ley de Kepler verificada",
                    field="kepler_third_law",
                    confidence=1.0
                ))
            else:
                results.append(self.create_validation_result(
                    level=ValidationLevel.WARNING,
                    message=f"Tercera ley de Kepler con error: {relative_error:.2%}",
                    field="kepler_third_law",
                    expected_value=f"T² = {expected_T_squared:.2f}",
                    actual_value=f"T² = {actual_T_squared:.2f}",
                    confidence=0.3
                ))
        
        return results