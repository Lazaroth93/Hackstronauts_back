# 🚀 Hackstronauts - Sistema de Análisis de Asteroides

Sistema de análisis de asteroides con agentes de IA que ejecuta simulaciones completas y genera reportes científicos.

## 🎯 Características

- **7 Agentes especializados** trabajando en secuencia
- **Análisis completo** de trayectoria, impacto y mitigación
- **Explicaciones científicas** en lenguaje natural
- **Predicciones ML** con confianza
- **API REST** con endpoints JSON
- **Niveles básico y técnico** de explicación

## 🛠️ Tecnologías

- **Backend**: FastAPI + Python 3.11
- **Agentes**: LangGraph + LangChain
- **Base de datos**: PostgreSQL
- **API**: NASA NEO API
- **Despliegue**: Render

## 🚀 Despliegue en Render

### Opción 1: Despliegue Automático

1. **Conecta tu repositorio** a Render
2. **Selecciona** "Web Service"
3. **Configuración**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: 3.11.9

### Opción 2: Usar render.yaml

El archivo `render.yaml` ya está configurado con:
- Servicio web
- Base de datos PostgreSQL
- Variables de entorno
- Configuración de producción

## 📡 Endpoints Disponibles

```
GET /health - Estado del sistema
GET /api/v1/explain/simulate/{neo_id}?level=basic
GET /api/v1/explain/simulate/{neo_id}?level=technical
```

## 🔧 Variables de Entorno

- `DATABASE_URL` - URL de PostgreSQL (automática en Render)
- `NASA_API_KEY` - Clave de la NASA API
- `API_HOST` - Host del servidor (0.0.0.0)
- `API_PORT` - Puerto del servidor ($PORT)
- `DEBUG` - Modo debug (False en producción)
- `ENVIRONMENT` - Entorno (production)

## 📊 Ejemplo de Uso

```bash
# Simulación básica
curl "https://tu-app.onrender.com/api/v1/explain/simulate/2000433?level=basic"

# Simulación técnica
curl "https://tu-app.onrender.com/api/v1/explain/simulate/2000433?level=technical"
```

## 🎯 Flujo de Agentes

1. **DataCollectorAgent** - Recolecta datos de asteroides
2. **TrajectoryAgent** - Analiza trayectoria orbital
3. **ImpactAnalyzerAgent** - Evalúa efectos de impacto
4. **MitigationAgent** - Evalúa estrategias de mitigación
5. **VisualizationAgent** - Genera visualizaciones
6. **ExplainerAgent** - Crea explicaciones científicas
7. **MLPredictorAgent** - Genera predicciones ML

## 📄 Estructura del JSON

```json
{
  "asteroid_id": "2000433",
  "simulation_results": {
    "status": "running",
    "asteroid_data": {...},
    "trajectory_analysis": {...},
    "impact_analysis": {...},
    "explanation_data": {...},
    "ml_predictions": {...}
  },
  "report_metadata": {
    "generated_at": "2024-10-05T11:52:52.202962",
    "level": "basic",
    "version": "1.0"
  }
}
```

## 🚀 Despliegue Rápido

1. **Sube el código** a GitHub
2. **Conecta** con Render
3. **Selecciona** el repositorio
4. **Render detecta** automáticamente la configuración
5. **¡Listo!** Tu API estará disponible

## 📞 Soporte

Para problemas con el despliegue, revisa los logs en Render Dashboard.
