@echo off
REM ============================================
REM Script de Inicio - Sistema de Comercializacion
REM ============================================

echo.
echo ======================================
echo   SISTEMA DE COMERCIALIZACION
echo ======================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor, instala Python 3.8 o superior
    pause
    exit /b 1
)

echo [OK] Python instalado
echo.

REM Verificar dependencias
echo Verificando dependencias...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [!] Streamlit no encontrado. Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencias instaladas
)

echo.
echo Verificando conexion a la base de datos...
python test_connection.py
if errorlevel 1 (
    echo.
    echo ERROR: No se pudo conectar a la base de datos
    echo Por favor, verifica:
    echo 1. MySQL esta corriendo
    echo 2. El archivo .env esta configurado correctamente
    echo 3. La base de datos existe
    echo.
    pause
    exit /b 1
)

echo.
echo ======================================
echo   INICIANDO APLICACION...
echo ======================================
echo.
echo La aplicacion se abrira automaticamente en tu navegador
echo Presiona Ctrl+C para detener el servidor
echo.

REM Iniciar Streamlit
streamlit run app.py

pause
