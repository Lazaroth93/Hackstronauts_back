"""
Script para configurar variables de entorno en Render
"""
import os

def setup_render_env():
    """Configura variables de entorno para Render"""
    
    # Variables básicas que siempre necesitamos
    env_vars = {
        'API_HOST': '0.0.0.0',
        'API_PORT': os.getenv('PORT', '8000'),
        'DEBUG': 'False',
        'ENVIRONMENT': 'production',
        'NASA_API_KEY': 'DEMO_KEY',
        'SECRET_KEY': 'hackstronauts_secret_key_2024',
        'LOG_LEVEL': 'INFO',
        'MAX_RETRIES': '3',
        'TIMEOUT_SECONDS': '30',
        'BATCH_SIZE': '100',
        'PLOTLY_THEME': 'plotly_dark',
        'MATPLOTLIB_STYLE': 'dark_background'
    }
    
    # Configurar variables de base de datos si no están definidas
    if not os.getenv('DATABASE_URL'):
        env_vars['DATABASE_URL'] = 'postgresql://postgres:password@localhost:5432/hackstronauts'
        env_vars['DB_HOST'] = 'localhost'
        env_vars['DB_PORT'] = '5432'
        env_vars['DB_NAME'] = 'hackstronauts'
        env_vars['DB_USER'] = 'postgres'
        env_vars['DB_PASSWORD'] = 'password'
    
    # Configurar variables de LangChain si no están definidas
    if not os.getenv('LANGCHAIN_API_KEY'):
        env_vars['LANGCHAIN_API_KEY'] = 'your_langchain_api_key_here'
        env_vars['LANGCHAIN_TRACING_V2'] = 'true'
        env_vars['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
    
    # Aplicar variables de entorno
    for key, value in env_vars.items():
        if not os.getenv(key):
            os.environ[key] = value
            print(f"✅ Configurado {key} = {value}")
    
    print("🎯 Variables de entorno configuradas para Render")

if __name__ == "__main__":
    setup_render_env()
