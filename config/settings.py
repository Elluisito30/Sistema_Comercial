"""
============================================
CONFIGURACIÓN GLOBAL DEL SISTEMA
============================================
Gestiona la carga de variables de entorno y 
proporciona acceso centralizado a configuraciones.

Autor: Sistema de Comercialización
Fecha: 2026
============================================
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ============================================
# CARGAR VARIABLES DE ENTORNO
# ============================================

# Obtener la ruta del directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar el archivo .env
ENV_FILE = BASE_DIR / '.env'
load_dotenv(ENV_FILE)

# ============================================
# CONFIGURACIÓN DE BASE DE DATOS - POSTGRESQL
# ============================================

class DatabaseConfig:
    """
    Configuración de conexión a PostgreSQL (Neon Cloud)
    """
    
    @staticmethod
    def get_database_url():
        """
        Obtiene la URL de conexión según el entorno.
        Prioriza Streamlit secrets, luego .env
        """
        try:
            import streamlit as st
            # En Streamlit Cloud
            return st.secrets["DATABASE_URL"]
        except:
            # En local
            return os.getenv("DATABASE_URL")
    
    # Configuración de Pool de Conexiones
    POOL_NAME = os.getenv('DB_POOL_NAME', 'postgres_pool')
    POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 10))
    
    @classmethod
    def get_config_dict(cls):
        """
        Retorna un diccionario con la configuración de conexión.
        Usa DATABASE_URL (DSN) para conectar a Neon.
        
        Returns:
            dict: Configuración para psycopg2.connect()
        """
        database_url = cls.get_database_url()
        
        if not database_url:
            raise ValueError(
                "DATABASE_URL no está configurada. "
                "Asegúrate de tener el archivo .env con DATABASE_URL "
                "o configurado en Streamlit secrets."
            )
        
        return {
            'dsn': database_url
        }
    
    @classmethod
    def get_pool_config(cls):
        """
        Retorna configuración para connection pooling.
        
        Returns:
            dict: Configuración del pool para psycopg2.pool
        """
        database_url = cls.get_database_url()
        
        if not database_url:
            raise ValueError(
                "DATABASE_URL no está configurada. "
                "Verifica tu archivo .env o Streamlit secrets."
            )
        
        return {
            'dsn': database_url,
            'maxconn': cls.POOL_SIZE
        }


# ============================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================

class AppConfig:
    """
    Configuración general de la aplicación
    """
    DEBUG = os.getenv('APP_DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('APP_SECRET_KEY', 'change-me-in-production')
    TIMEZONE = os.getenv('TIMEZONE', 'America/Lima')
    
    # Directorios de la aplicación
    BASE_DIR = BASE_DIR
    REPORTS_DIR = BASE_DIR / 'reports'
    LOGS_DIR = BASE_DIR / 'logs'
    UPLOADS_DIR = BASE_DIR / 'uploads'
    
    @classmethod
    def create_directories(cls):
        """
        Crea los directorios necesarios si no existen
        """
        cls.REPORTS_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.UPLOADS_DIR.mkdir(exist_ok=True)


# ============================================
# CONSTANTES DEL SISTEMA
# ============================================

class Constants:
    """
    Constantes utilizadas en todo el sistema
    """
    # Estados de compras
    COMPRA_ESTADO_PENDIENTE = 'pendiente'
    COMPRA_ESTADO_RECIBIDA = 'recibida'
    COMPRA_ESTADO_CANCELADA = 'cancelada'
    
    # Estados de ventas
    VENTA_ESTADO_COMPLETADA = 'completada'
    VENTA_ESTADO_ANULADA = 'anulada'
    
    # Tipos de movimiento de inventario
    MOVIMIENTO_ENTRADA = 'entrada'
    MOVIMIENTO_SALIDA = 'salida'
    MOVIMIENTO_AJUSTE = 'ajuste'
    
    # Roles de usuario
    ROL_ADMIN = 'admin'
    ROL_VENDEDOR = 'vendedor'
    ROL_ALMACENERO = 'almacenero'
    
    # Tipos de comprobante
    COMPROBANTE_BOLETA = 'boleta'
    COMPROBANTE_FACTURA = 'factura'
    COMPROBANTE_TICKET = 'ticket'
    
    # Métodos de pago
    PAGO_EFECTIVO = 'efectivo'
    PAGO_TARJETA = 'tarjeta'
    PAGO_TRANSFERENCIA = 'transferencia'


# ============================================
# VALIDACIÓN DE CONFIGURACIÓN
# ============================================

def validate_config():
    """
    Valida que las configuraciones críticas estén presentes
    
    Raises:
        ValueError: Si falta alguna configuración crítica
    """
    errors = []
    
    # Verificar DATABASE_URL
    try:
        database_url = DatabaseConfig.get_database_url()
        if not database_url:
            errors.append("DATABASE_URL no está configurado en .env o Streamlit secrets")
    except Exception as e:
        errors.append(f"Error al obtener DATABASE_URL: {e}")
    
    if AppConfig.SECRET_KEY == 'change-me-in-production' and not AppConfig.DEBUG:
        errors.append("APP_SECRET_KEY debe cambiarse en producción")
    
    if errors:
        raise ValueError(f"Errores de configuración:\n" + "\n".join(f"- {e}" for e in errors))


# Validar configuración al importar
if __name__ != '__main__':
    validate_config()
    AppConfig.create_directories()