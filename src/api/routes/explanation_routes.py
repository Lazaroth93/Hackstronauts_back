"""
Rutas para Explicaciones Científicas
Maneja las peticiones HTTP para generar explicaciones comprensibles
"""

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import FileResponse
from typing import Optional
import tempfile
import os
from datetime import datetime

from ..controllers.explanation_controller import ExplanationController
from ..models.explanation_models import (
    CompleteExplanationResponse,
    AsteroidBasicResponse,
    ImpactExplanationResponse,
    TrajectoryExplanationResponse,
    MitigationExplanationResponse,
    RiskOverviewResponse
)

# Crear el router para explicaciones
explanation_router = APIRouter(prefix="/explain", tags=["Explicaciones"])

# Instancia del controlador (se inicializa solo cuando se necesita)
def get_explanation_controller():
    """Obtiene una instancia del controlador de explicaciones"""
    return ExplanationController()

@explanation_router.get("/asteroid/{neo_id}", response_model=CompleteExplanationResponse)
async def get_complete_explanation(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera explicación completa del asteroide
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Explicación completa con todos los análisis científicos
    """
    try:
        controller = get_explanation_controller()
        result = controller.get_complete_explanation(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando explicación completa: {str(e)}")

@explanation_router.get("/asteroid/{neo_id}/basics", response_model=AsteroidBasicResponse)
async def get_asteroid_basics(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera explicación básica del asteroide
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Explicación básica con tamaño, peligro y clasificación
    """
    try:
        controller = get_explanation_controller()
        result = controller.get_asteroid_basic_explanation(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando explicación básica: {str(e)}")

@explanation_router.get("/asteroid/{neo_id}/impact", response_model=ImpactExplanationResponse)
async def get_impact_explanation(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera explicación de efectos de impacto
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Explicación de impacto con comparaciones históricas
    """
    try:
        controller = get_explanation_controller()
        result = controller.get_impact_explanation(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando explicación de impacto: {str(e)}")

@explanation_router.get("/asteroid/{neo_id}/trajectory", response_model=TrajectoryExplanationResponse)
async def get_trajectory_explanation(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera explicación de trayectoria orbital
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Explicación de trayectoria con predicciones futuras
    """
    try:
        controller = get_explanation_controller()
        result = controller.get_trajectory_explanation(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando explicación de trayectoria: {str(e)}")

@explanation_router.get("/asteroid/{neo_id}/mitigation", response_model=MitigationExplanationResponse)
async def get_mitigation_explanation(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera explicación de estrategias de mitigación
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Explicación de mitigación con estrategias factibles
    """
    try:
        controller = get_explanation_controller()
        result = controller.get_mitigation_explanation(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando explicación de mitigación: {str(e)}")

@explanation_router.get("/asteroid/{neo_id}/risk", response_model=RiskOverviewResponse)
async def get_risk_overview(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera resumen general de riesgo
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Resumen de riesgo con recomendaciones
    """
    try:
        controller = get_explanation_controller()
        result = controller.get_risk_overview(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando resumen de riesgo: {str(e)}")

# Endpoint de salud específico para explicaciones
@explanation_router.get("/health")
async def explanation_health_check():
    """
    Verifica el estado del servicio de explicaciones
    
    Returns:
        Estado del servicio y estadísticas de explicaciones
    """
    try:
        controller = get_explanation_controller()
        
        return {
            "status": "healthy",
            "service": "Explicaciones Científicas",
            "supported_explanations": [
                "asteroid_basics",
                "impact_analysis",
                "trajectory_analysis", 
                "mitigation_analysis",
                "risk_overview",
                "complete"
            ],
            "features": [
                "Explicaciones en lenguaje natural",
                "Comparaciones históricas",
                "Clasificaciones científicas",
                "Evaluaciones de riesgo",
                "Predicciones futuras"
            ],
            "timestamp": "2024-09-30T18:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Servicio de explicaciones no disponible: {str(e)}")

@explanation_router.get("/asteroid/{neo_id}/pdf")
async def generate_pdf_report(
    neo_id: str = Path(..., description="ID único del NEO"),
    level: str = Query("basic", description="Nivel de explicación: 'basic' o 'technical'")
):
    """
    Genera reporte PDF del asteroide
    
    - **neo_id**: ID único del NEO
    - **level**: Nivel de explicación
        - `basic`: Para público general (lenguaje simple)
        - `technical`: Para científicos y gobiernos (métricas detalladas)
    
    Returns:
        Archivo PDF con el reporte completo
    """
    try:
        # Validar nivel
        if level not in ["basic", "technical"]:
            raise HTTPException(
                status_code=400, 
                detail="Nivel debe ser 'basic' o 'technical'"
            )
        
        # Generar PDF directamente (sin base de datos por ahora)
        pdf_path = await generate_simple_pdf(neo_id, level)
        
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=404, 
                detail=f"No se pudo generar el PDF para el NEO {neo_id}"
            )
        
        # Determinar nombre del archivo
        filename = f"asteroid_report_{neo_id}_{level}.pdf"
        
        # Devolver archivo PDF
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generando PDF: {str(e)}"
        )

@explanation_router.get("/simulate-and-pdf/{neo_id}")
async def simulate_and_generate_pdf(
    neo_id: str = Path(..., description="ID único del NEO"),
    level: str = Query("basic", description="Nivel de explicación: 'basic' o 'technical'")
):
    """
    Ejecuta simulación completa del asteroide y genera PDF
    
    - **neo_id**: ID único del NEO
    - **level**: Nivel de explicación ('basic' o 'technical')
    
    Returns:
        Archivo PDF con el reporte completo de la simulación
    """
    try:
        # Validar nivel
        if level not in ["basic", "technical"]:
            raise HTTPException(
                status_code=400, 
                detail="Nivel debe ser 'basic' o 'technical'"
            )
        
        # Importar componentes del sistema
        from ...graphs.graph_agent import AgentGraph
        from ...supervisors.hybrid_supervisor import HybridSupervisor
        
        # Datos de prueba del asteroide
        asteroid_data = {
            "id": neo_id,
            "name": f"Asteroid {neo_id}",
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
        
        # Ejecutar simulación completa
        print(f"🚀 Iniciando simulación completa para {neo_id}...")
        supervisor = HybridSupervisor()
        agent_graph = AgentGraph(supervisor=supervisor)
        
        simulation_result = await agent_graph.run_simulation(
            asteroid_data=asteroid_data,
            simulation_params={"level": level}
        )
        
        # Generar PDF con los resultados de la simulación
        pdf_path = await generate_pdf_from_simulation(neo_id, level, simulation_result)
        
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=404, 
                detail=f"No se pudo generar el PDF para el NEO {neo_id}"
            )
        
        # Determinar nombre del archivo
        filename = f"asteroid_simulation_{neo_id}_{level}.pdf"
        
        # Devolver archivo PDF
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error en simulación y generación de PDF: {str(e)}"
        )

@explanation_router.get("/simulate/{neo_id}")
async def simulate_asteroid_json(
    neo_id: str = Path(..., description="ID único del NEO"),
    level: str = Query("basic", description="Nivel de explicación: 'basic' o 'technical'")
):
    """
    Ejecuta simulación completa del asteroide y devuelve JSON
    
    - **neo_id**: ID único del NEO
    - **level**: Nivel de explicación ('basic' o 'technical')
    
    Returns:
        JSON con todos los resultados de la simulación
    """
    try:
        # Validar nivel
        if level not in ["basic", "technical"]:
            raise HTTPException(
                status_code=400, 
                detail="Nivel debe ser 'basic' o 'technical'"
            )
        
        # Importar componentes del sistema
        from ...graphs.graph_agent import AgentGraph
        from ...supervisors.hybrid_supervisor import HybridSupervisor
        
        # Datos de prueba del asteroide
        asteroid_data = {
            "id": neo_id,
            "name": f"Asteroid {neo_id}",
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
        
        # Ejecutar simulación completa
        print(f"🚀 Iniciando simulación completa para {neo_id}...")
        supervisor = HybridSupervisor()
        agent_graph = AgentGraph(supervisor=supervisor)
        
        simulation_result = await agent_graph.run_simulation(
            asteroid_data=asteroid_data,
            simulation_params={"level": level}
        )
        
        # Construir respuesta JSON estructurada
        response = {
            "asteroid_id": neo_id,
            "simulation_results": {
                "status": simulation_result.status,
                "current_step": simulation_result.current_step,
                "asteroid_data": simulation_result.asteroid_data,
                "data_collection_result": simulation_result.data_collection_result,
                "trajectory_analysis": simulation_result.trajectory_analysis,
                "impact_analysis": simulation_result.impact_analysis,
                "mitigation_strategies": simulation_result.mitigation_strategies,
                "mitigation_analysis": simulation_result.mitigation_analysis,
                "visualization_data": simulation_result.visualization_data,
                "explanation_data": simulation_result.explanation_data,
                "ml_predictions": simulation_result.ml_predictions,
                "errors": simulation_result.errors,
                "warnings": simulation_result.warnings
            },
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "level": level,
                "version": "1.0",
                "simulation_type": "complete_analysis"
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error en simulación: {str(e)}"
        )

@explanation_router.get("/test-pdf")
async def test_pdf_generation():
    """Endpoint de prueba para verificar que la generación de PDF funciona"""
    try:
        pdf_path = await generate_simple_pdf("TEST", "basic")
        
        if not pdf_path or not os.path.exists(pdf_path):
            return {"error": "No se pudo generar PDF de prueba"}
        
        return FileResponse(
            path=pdf_path,
            filename="test_report.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        return {"error": f"Error en prueba: {str(e)}"}

async def generate_simple_pdf(neo_id: str, level: str) -> Optional[str]:
    """Genera un PDF simple sin base de datos"""
    try:
        import tempfile
        import os
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from datetime import datetime
        
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_path = temp_file.name
        temp_file.close()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(temp_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Centrado
        )
        
        story.append(Paragraph(f"REPORTE DE ASTEROIDE - {neo_id}", title_style))
        story.append(Spacer(1, 20))
        
        # Información del nivel
        level_text = "BÁSICO" if level == "basic" else "TÉCNICO"
        story.append(Paragraph(f"Nivel: {level_text}", styles['Normal']))
        story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Contenido según nivel
        if level == "basic":
            story.append(Paragraph("RESUMEN EJECUTIVO", styles['Heading2']))
            story.append(Paragraph(
                "Este reporte proporciona una explicación clara y comprensible sobre el asteroide analizado, "
                "incluyendo su nivel de riesgo y las recomendaciones correspondientes.",
                styles['Normal']
            ))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("DATOS BÁSICOS", styles['Heading2']))
            story.append(Paragraph("• Tamaño: Similar a una montaña pequeña", styles['Normal']))
            story.append(Paragraph("• Riesgo: BAJO - No requiere acción inmediata", styles['Normal']))
            story.append(Paragraph("• Monitoreo: Continuar observación rutinaria", styles['Normal']))
            
        else:  # technical
            story.append(Paragraph("ANÁLISIS TÉCNICO DETALLADO", styles['Heading2']))
            story.append(Paragraph(
                "Este reporte contiene métricas precisas, parámetros orbitales y análisis científicos "
                "detallados para uso de especialistas y organismos gubernamentales.",
                styles['Normal']
            ))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("PARÁMETROS ORBITALES", styles['Heading2']))
            story.append(Paragraph("• Semi-eje mayor: 1.458 UA", styles['Normal']))
            story.append(Paragraph("• Excentricidad: 0.2227", styles['Normal']))
            story.append(Paragraph("• Inclinación: 10.829°", styles['Normal']))
            story.append(Paragraph("• Perihelio: 1.133 UA", styles['Normal']))
            story.append(Paragraph("• Afelio: 1.783 UA", styles['Normal']))
            story.append(Spacer(1, 20))
            
            story.append(Paragraph("ANÁLISIS DE ENERGÍA CINÉTICA", styles['Heading2']))
            story.append(Paragraph("• Energía cinética: 2.5 × 10¹⁵ J", styles['Normal']))
            story.append(Paragraph("• Equivalente TNT: 0.6 Megatones", styles['Normal']))
            story.append(Paragraph("• Radio de destrucción: 15 km", styles['Normal']))
        
        # Construir PDF
        doc.build(story)
        
        return temp_path
        
    except Exception as e:
        print(f"Error generando PDF simple: {e}")
        import traceback
        traceback.print_exc()
        return None

async def generate_pdf_from_simulation(neo_id: str, level: str, simulation_result) -> Optional[str]:
    """Genera PDF basado en los resultados de la simulación"""
    try:
        import tempfile
        import os
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from datetime import datetime
        
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_path = temp_file.name
        temp_file.close()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(temp_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Centrado
        )
        
        story.append(Paragraph(f"REPORTE DE SIMULACIÓN - ASTEROIDE {neo_id}", title_style))
        story.append(Spacer(1, 20))
        
        # Información del nivel
        level_text = "BÁSICO" if level == "basic" else "TÉCNICO"
        story.append(Paragraph(f"Nivel: {level_text}", styles['Normal']))
        story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Estado de simulación: {simulation_result.status}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Resultados de la simulación
        story.append(Paragraph("RESULTADOS DE LA SIMULACIÓN", styles['Heading2']))
        
        # Datos del asteroide
        if hasattr(simulation_result, 'asteroid_data') and simulation_result.asteroid_data:
            story.append(Paragraph("DATOS DEL ASTEROIDE", styles['Heading3']))
            asteroid_data = simulation_result.asteroid_data
            story.append(Paragraph(f"• Nombre: {asteroid_data.get('name', 'Desconocido')}", styles['Normal']))
            story.append(Paragraph(f"• Diámetro: {asteroid_data.get('diameter_min', 0)} km", styles['Normal']))
            story.append(Paragraph(f"• Peligroso: {'Sí' if asteroid_data.get('is_potentially_hazardous', False) else 'No'}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Análisis de trayectoria
        if hasattr(simulation_result, 'trajectory_analysis') and simulation_result.trajectory_analysis:
            story.append(Paragraph("ANÁLISIS DE TRAYECTORIA", styles['Heading3']))
            story.append(Paragraph("• Trayectoria orbital calculada exitosamente", styles['Normal']))
            story.append(Paragraph("• Parámetros orbitales analizados", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Análisis de impacto
        if hasattr(simulation_result, 'impact_analysis') and simulation_result.impact_analysis:
            story.append(Paragraph("ANÁLISIS DE IMPACTO", styles['Heading3']))
            story.append(Paragraph("• Efectos de impacto evaluados", styles['Normal']))
            story.append(Paragraph("• Energía cinética calculada", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Estrategias de mitigación
        if hasattr(simulation_result, 'mitigation_analysis') and simulation_result.mitigation_analysis:
            story.append(Paragraph("ESTRATEGIAS DE MITIGACIÓN", styles['Heading3']))
            story.append(Paragraph("• Opciones de mitigación evaluadas", styles['Normal']))
            story.append(Paragraph("• Viabilidad técnica analizada", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Explicaciones científicas
        if hasattr(simulation_result, 'explanation_data') and simulation_result.explanation_data:
            story.append(Paragraph("EXPLICACIONES CIENTÍFICAS", styles['Heading3']))
            explanation_data = simulation_result.explanation_data
            if isinstance(explanation_data, dict) and 'results' in explanation_data:
                for key, explanation in explanation_data['results'].items():
                    if isinstance(explanation, dict):
                        for sub_key, sub_value in explanation.items():
                            story.append(Paragraph(f"• {sub_key}: {sub_value}", styles['Normal']))
                    else:
                        story.append(Paragraph(f"• {key}: {explanation}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Predicciones ML
        if hasattr(simulation_result, 'ml_predictions') and simulation_result.ml_predictions:
            story.append(Paragraph("PREDICCIONES DE MACHINE LEARNING", styles['Heading3']))
            ml_data = simulation_result.ml_predictions
            if isinstance(ml_data, dict):
                for key, value in ml_data.items():
                    story.append(Paragraph(f"• {key}: {value}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Errores y advertencias
        if hasattr(simulation_result, 'errors') and simulation_result.errors:
            story.append(Paragraph("ERRORES ENCONTRADOS", styles['Heading3']))
            for error in simulation_result.errors:
                story.append(Paragraph(f"• {error}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        if hasattr(simulation_result, 'warnings') and simulation_result.warnings:
            story.append(Paragraph("ADVERTENCIAS", styles['Heading3']))
            for warning in simulation_result.warnings:
                story.append(Paragraph(f"• {warning}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Resumen final
        story.append(Paragraph("RESUMEN FINAL", styles['Heading2']))
        if level == "basic":
            story.append(Paragraph(
                "Este reporte proporciona una explicación clara y comprensible sobre el asteroide analizado, "
                "incluyendo su nivel de riesgo y las recomendaciones correspondientes.",
                styles['Normal']
            ))
        else:
            story.append(Paragraph(
                "Este reporte contiene métricas precisas, parámetros orbitales y análisis científicos "
                "detallados para uso de especialistas y organismos gubernamentales.",
                styles['Normal']
            ))
        
        # Construir PDF
        doc.build(story)
        
        return temp_path
        
    except Exception as e:
        print(f"Error generando PDF desde simulación: {e}")
        import traceback
        traceback.print_exc()
        return None