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
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================

class DatabaseConfig:
    """
    Configuración de conexión a MySQL
    """
    HOST = os.getenv('DB_HOST', 'localhost')
    PORT = int(os.getenv('DB_PORT', 3306))
    USER = os.getenv('DB_USER', 'root')
    PASSWORD = os.getenv('DB_PASSWORD', '')
    NAME = os.getenv('DB_NAME', 'sistema_comercializacion')
    
    # Configuración de Pool de Conexiones
    POOL_NAME = os.getenv('DB_POOL_NAME', 'mypool')
    POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 5))
    
    @classmethod
    def get_config_dict(cls):
        """
        Retorna un diccionario con la configuración de conexión
        
        Returns:
            dict: Configuración para mysql.connector
        """
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'user': cls.USER,
            'password': cls.PASSWORD,
            'database': cls.NAME,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': False,  # Control manual de transacciones
            'raise_on_warnings': True
        }
    
    @classmethod
    def get_pool_config(cls):
        """
        Retorna configuración para connection pooling
        
        Returns:
            dict: Configuración del pool
        """
        config = cls.get_config_dict()
        config.update({
            'pool_name': cls.POOL_NAME,
            'pool_size': cls.POOL_SIZE,
            'pool_reset_session': True
        })
        return config


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
    
    if not DatabaseConfig.HOST:
        errors.append("DB_HOST no está configurado")
    
    if not DatabaseConfig.USER:
        errors.append("DB_USER no está configurado")
    
    if not DatabaseConfig.NAME:
        errors.append("DB_NAME no está configurado")
    
    if AppConfig.SECRET_KEY == 'change-me-in-production' and not AppConfig.DEBUG:
        errors.append("APP_SECRET_KEY debe cambiarse en producción")
    
    if errors:
        raise ValueError(f"Errores de configuración:\n" + "\n".join(f"- {e}" for e in errors))


# Validar configuración al importar
if __name__ != '__main__':
    validate_config()
    AppConfig.create_directories()