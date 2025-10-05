"""
Script de prueba para el sistema Hackstronauts
Ejecuta una simulación completa de asteroide
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.graphs.graph_agent import AgentGraph
from src.supervisors.hybrid_supervisor import HybridSupervisor

async def test_asteroid_simulation():
    """Prueba una simulación completa de asteroide"""
    
    print("🚀 HACKSTRONAUTS - PRUEBA DE SIMULACIÓN COMPLETA")
    print("=" * 60)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Datos de prueba de un asteroide real (Eros)
    test_asteroid_data = {
        "id": "2000433",
        "name": "Eros",
        "diameter_min": 16.84,  # km
        "diameter_max": 16.84,  # km
        "is_potentially_hazardous": False,
        "close_approach_data": [
            {
                "close_approach_date": "2024-12-25",
                "miss_distance": {"kilometers": "0.2"},
                "relative_velocity": {"kilometers_per_hour": "12345.67"},
                "orbiting_body": "Earth"
            }
        ],
        "orbital_data": {
            "eccentricity": "0.2227",
            "inclination": "10.829",
            "semi_major_axis": "1.458",
            "perihelion_distance": "1.133",
            "aphelion_distance": "1.783"
        },
        "physical_characteristics": {
            "absolute_magnitude": 11.16,
            "albedo": 0.25,
            "spectral_type": "S"
        }
    }
    
    # Parámetros de simulación
    simulation_params = {
        "simulation_type": "complete_analysis",
        "include_mitigation": True,
        "include_visualization": True,
        "confidence_threshold": 0.8
    }
    
    try:
        # Inicializar supervisor
        print("🔧 Inicializando supervisor híbrido...")
        supervisor = HybridSupervisor()
        
        # Inicializar grafo de agentes
        print("🤖 Inicializando grafo de agentes...")
        agent_graph = AgentGraph(supervisor=supervisor)
        
        # Ejecutar simulación
        print("🎯 Iniciando simulación de asteroide...")
        print(f"📋 Asteroide: {test_asteroid_data['name']} (ID: {test_asteroid_data['id']})")
        print(f"📏 Diámetro: {test_asteroid_data['diameter_min']} km")
        print(f"⚠️ Peligroso: {'Sí' if test_asteroid_data['is_potentially_hazardous'] else 'No'}")
        print("-" * 60)
        
        # Ejecutar la simulación completa
        result_state = await agent_graph.run_simulation(
            asteroid_data=test_asteroid_data,
            simulation_params=simulation_params
        )
        
        # Mostrar resultados
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DE LA SIMULACIÓN")
        print("=" * 60)
        
        print(f"✅ Estado: {result_state.status}")
        print(f"📈 Pasos completados: {result_state.current_step}")
        
        if result_state.errors:
            print(f"❌ Errores: {len(result_state.errors)}")
            for error in result_state.errors:
                print(f"   - {error}")
        
        if result_state.warnings:
            print(f"⚠️ Advertencias: {len(result_state.warnings)}")
            for warning in result_state.warnings:
                print(f"   - {warning}")
        
        # Mostrar datos de explicación si están disponibles
        if hasattr(result_state, 'explanation_data') and result_state.explanation_data:
            print("\n📚 EXPLICACIONES GENERADAS:")
            print("-" * 40)
            explanation_data = result_state.explanation_data
            if isinstance(explanation_data, dict) and 'results' in explanation_data:
                for key, explanation in explanation_data['results'].items():
                    print(f"🔹 {key}: {explanation}")
        
        print(f"\n⏰ Completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        return result_state
        
    except Exception as e:
        print(f"❌ Error durante la simulación: {str(e)}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        import traceback
        print("📋 Traceback completo:")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🧪 Iniciando prueba del sistema Hackstronauts...")
    asyncio.run(test_asteroid_simulation())
