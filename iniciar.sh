#!/bin/bash
# ============================================
# Script de Inicio - Sistema de Comercializacion
# ============================================

echo ""
echo "======================================"
echo "   SISTEMA DE COMERCIALIZACION"
echo "======================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado"
    echo "Por favor, instala Python 3.8 o superior"
    exit 1
fi

echo "[OK] Python instalado"
echo ""

# Verificar dependencias
echo "Verificando dependencias..."
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "[!] Streamlit no encontrado. Instalando dependencias..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudieron instalar las dependencias"
        exit 1
    fi
else
    echo "[OK] Dependencias instaladas"
fi

echo ""
echo "Verificando conexión a la base de datos..."
python3 test_connection.py
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: No se pudo conectar a la base de datos"
    echo "Por favor, verifica:"
    echo "1. MySQL está corriendo"
    echo "2. El archivo .env está configurado correctamente"
    echo "3. La base de datos existe"
    echo ""
    exit 1
fi

echo ""
echo "======================================"
echo "   INICIANDO APLICACIÓN..."
echo "======================================"
echo ""
echo "La aplicación se abrirá automáticamente en tu navegador"
echo "Presiona Ctrl+C para detener el servidor"
echo ""

# Iniciar Streamlit
streamlit run app.py
