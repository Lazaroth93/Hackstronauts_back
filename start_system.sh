#!/bin/bash

# Hackstronauts - Script de inicio del sistema
# Este script configura y ejecuta el sistema sin Docker

set -e  # Salir si hay algún error

echo "🚀 Iniciando Hackstronauts - Sistema de Análisis de Asteroides"
echo "=============================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con color
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si Python está instalado
print_status "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado. Por favor instala Python 3.11 o superior."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
print_success "Python $PYTHON_VERSION encontrado"

# Verificar si el entorno virtual existe
print_status "Verificando entorno virtual..."
if [ ! -d "venv" ]; then
    print_warning "Entorno virtual no encontrado. Creando uno nuevo..."
    python3 -m venv venv
    print_success "Entorno virtual creado"
fi

# Activar entorno virtual
print_status "Activando entorno virtual..."
source venv/bin/activate
print_success "Entorno virtual activado"

# Verificar si requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt no encontrado"
    exit 1
fi

# Instalar dependencias
print_status "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Dependencias instaladas"

# Verificar archivo .env
print_status "Verificando configuración..."
if [ ! -f ".env" ]; then
    print_warning "Archivo .env no encontrado. Creando uno desde .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "IMPORTANTE: Edita el archivo .env con tus configuraciones reales"
    else
        print_error "No se encontró .env.example. Por favor crea un archivo .env"
        exit 1
    fi
fi

# Crear directorio de logs si no existe
mkdir -p logs

# Verificar PostgreSQL (opcional)
print_status "Verificando PostgreSQL..."
if command -v psql &> /dev/null; then
    print_success "PostgreSQL encontrado"
else
    print_warning "PostgreSQL no encontrado. Asegúrate de tenerlo instalado y configurado"
fi

# Mostrar configuración
print_status "Configuración del sistema:"
echo "  - Host: ${API_HOST:-0.0.0.0}"
echo "  - Puerto: ${API_PORT:-8000}"
echo "  - Debug: ${DEBUG:-True}"
echo "  - Entorno: ${ENVIRONMENT:-development}"

# Preguntar si quiere continuar
echo ""
read -p "¿Continuar con el inicio del sistema? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Inicio cancelado"
    exit 0
fi

# Iniciar el sistema
print_status "Iniciando Hackstronauts..."
echo ""
print_success "Sistema iniciado correctamente!"
print_status "Accede a: http://localhost:${API_PORT:-8000}"
print_status "Documentación API: http://localhost:${API_PORT:-8000}/docs"
print_status "Presiona Ctrl+C para detener el sistema"
echo ""

# Ejecutar el sistema
python main.py
