"""
============================================
CAPA DE CONEXIÓN A BASE DE DATOS - POSTGRESQL
============================================
Proporciona funciones para gestionar conexiones
a PostgreSQL de forma segura y eficiente.

Características:
- Connection pooling para mejor rendimiento
- Manejo robusto de errores
- Funciones reutilizables
- Logging de operaciones

Autor: Sistema de Comercialización
Fecha: 2026
============================================
"""

import psycopg2
from psycopg2 import pool, OperationalError
from psycopg2.extras import RealDictCursor, DictCursor
from contextlib import contextmanager
import logging
from typing import Optional, Dict, Any, List, Tuple
from config.settings import DatabaseConfig

# ============================================
# CONFIGURACIÓN DE LOGGING
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/database.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ============================================
# POOL DE CONEXIONES GLOBAL
# ============================================

_connection_pool: Optional[pool.SimpleConnectionPool] = None


def initialize_pool():
    """
    Inicializa el pool de conexiones a PostgreSQL.
    
    Esta función debe llamarse una vez al inicio de la aplicación.
    Crea un pool de conexiones reutilizables para mejorar el rendimiento.
    
    Raises:
        OperationalError: Si no se puede crear el pool de conexiones
    """
    global _connection_pool
    
    if _connection_pool is not None:
        logger.warning("El pool de conexiones ya está inicializado")
        return
    
    try:
        logger.info("Inicializando pool de conexiones a PostgreSQL...")
        
        pool_config = DatabaseConfig.get_pool_config()
        
        _connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=pool_config['maxconn'],
            dsn=pool_config['dsn']
        )
        
        logger.info(
            f"Pool de conexiones creado exitosamente "
            f"(size={pool_config['maxconn']})"
        )
        
        # Probar la conexión
        test_connection()
        
    except OperationalError as e:
        logger.error(f"Error al crear el pool de conexiones: {e}")
        _connection_pool = None
        raise


def get_connection():
    """
    Obtiene una conexión del pool.
    
    Esta es la función principal que debe usarse para obtener conexiones
    en todo el sistema. Utiliza el pool de conexiones si está disponible,
    o crea una conexión directa como fallback.
    
    Returns:
        psycopg2.extensions.connection: Conexión a la base de datos
        
    Raises:
        OperationalError: Si no se puede obtener una conexión
        
    Example:
        >>> conn = get_connection()
        >>> cursor = conn.cursor(cursor_factory=RealDictCursor)
        >>> cursor.execute("SELECT * FROM usuarios")
        >>> results = cursor.fetchall()
        >>> cursor.close()
        >>> conn.close()
    """
    global _connection_pool
    
    try:
        # Intentar obtener conexión del pool
        if _connection_pool is not None:
            connection = _connection_pool.getconn()
            logger.debug("Conexión obtenida del pool")
            return connection
        
        # Fallback: crear conexión directa si no hay pool
        logger.warning("Pool no disponible, creando conexión directa")
        config = DatabaseConfig.get_config_dict()
        connection = psycopg2.connect(config['dsn'])
        return connection
        
    except OperationalError as e:
        logger.error(f"Error al obtener conexión: {e}")
        raise


@contextmanager
def get_db_connection():
    """
    Context manager para manejar conexiones automáticamente.
    
    Garantiza que la conexión se cierre correctamente incluso si
    ocurre una excepción. Uso recomendado para operaciones simples.
    
    Yields:
        psycopg2.extensions.connection: Conexión a la base de datos
        
    Example:
        >>> with get_db_connection() as conn:
        ...     cursor = conn.cursor(cursor_factory=RealDictCursor)
        ...     cursor.execute("SELECT * FROM productos")
        ...     productos = cursor.fetchall()
        ...     cursor.close()
    """
    connection = None
    try:
        connection = get_connection()
        yield connection
    except OperationalError as e:
        logger.error(f"Error en la conexión: {e}")
        raise
    finally:
        if connection:
            if _connection_pool:
                _connection_pool.putconn(connection)
            else:
                connection.close()
            logger.debug("Conexión cerrada correctamente")


@contextmanager
def get_db_cursor(dictionary=True, buffered=True):
    """
    Context manager que proporciona cursor y conexión juntos.
    
    Maneja automáticamente la apertura/cierre de conexión y cursor.
    Ideal para operaciones de lectura simples.
    
    Args:
        dictionary (bool): Si True, los resultados se retornan como diccionarios
        buffered (bool): No aplica directamente en PostgreSQL, pero se mantiene para compatibilidad
        
    Yields:
        tuple: (cursor, connection)
        
    Example:
        >>> with get_db_cursor() as (cursor, conn):
        ...     cursor.execute("SELECT * FROM categorias")
        ...     categorias = cursor.fetchall()
        ...     for cat in categorias:
        ...         print(cat['nombre'])
    """
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor_factory = RealDictCursor if dictionary else None
        cursor = connection.cursor(cursor_factory=cursor_factory)
        yield cursor, connection
    except OperationalError as e:
        logger.error(f"Error en cursor: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            if _connection_pool:
                _connection_pool.putconn(connection)
            else:
                connection.close()


def execute_query(query: str, params: tuple = None, fetch: str = 'all') -> Optional[Any]:
    """
    Ejecuta una consulta SELECT y retorna los resultados.
    
    Función de conveniencia para consultas simples de lectura.
    
    Args:
        query (str): Consulta SQL a ejecutar
        params (tuple, optional): Parámetros para la consulta
        fetch (str): Tipo de fetch - 'all', 'one', 'many'
        
    Returns:
        list|dict|None: Resultados de la consulta
        
    Example:
        >>> usuarios = execute_query("SELECT * FROM usuarios WHERE activo = %s", (True,))
        >>> usuario = execute_query(
        ...     "SELECT * FROM usuarios WHERE id = %s", 
        ...     (1,), 
        ...     fetch='one'
        ... )
    """
    try:
        with get_db_cursor() as (cursor, conn):
            cursor.execute(query, params or ())
            
            if fetch == 'one':
                result = cursor.fetchone()
            elif fetch == 'many':
                result = cursor.fetchmany()
            else:  # 'all'
                result = cursor.fetchall()
            
            logger.debug(f"Query ejecutado: {query[:100]}...")
            return result
            
    except OperationalError as e:
        logger.error(f"Error ejecutando query: {e}")
        logger.error(f"Query: {query}")
        raise


def execute_transaction(operations: List[Tuple[str, tuple]]) -> bool:
    """
    Ejecuta múltiples operaciones en una transacción.
    
    Garantiza atomicidad: todas las operaciones se ejecutan o ninguna.
    Útil para operaciones complejas como ventas con múltiples detalles.
    
    Args:
        operations (list): Lista de tuplas (query, params)
        
    Returns:
        bool: True si la transacción fue exitosa
        
    Example:
        >>> operations = [
        ...     ("INSERT INTO ventas (...) VALUES (...)", (datos_venta,)),
        ...     ("INSERT INTO detalle_ventas (...) VALUES (...)", (datos_detalle,)),
        ...     ("UPDATE productos SET stock_actual = stock_actual - %s WHERE id = %s", (cantidad, producto_id))
        ... ]
        >>> success = execute_transaction(operations)
    """
    connection = None
    cursor = None
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # Iniciar transacción (autocommit=False por defecto en psycopg2)
        logger.debug("Transacción iniciada")
        
        # Ejecutar todas las operaciones
        for query, params in operations:
            cursor.execute(query, params or ())
            logger.debug(f"Operación ejecutada: {query[:80]}...")
        
        # Confirmar transacción
        connection.commit()
        logger.info(f"Transacción completada: {len(operations)} operaciones")
        return True
        
    except OperationalError as e:
        # Revertir en caso de error
        if connection:
            connection.rollback()
            logger.error(f"Transacción revertida debido a error: {e}")
        raise
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            if _connection_pool:
                _connection_pool.putconn(connection)
            else:
                connection.close()


def test_connection() -> bool:
    """
    Prueba la conexión a la base de datos.
    
    Útil para diagnóstico y validación de configuración.
    
    Returns:
        bool: True si la conexión es exitosa
        
    Raises:
        OperationalError: Si no se puede conectar
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            cursor.execute("SELECT current_database()")
            db_name = cursor.fetchone()
            cursor.close()
            
            logger.info(f"Conexión exitosa a PostgreSQL - Versión: {version[0][:50]}...")
            logger.info(f"Base de datos: {db_name[0]}")
            return True
            
    except OperationalError as e:
        logger.error(f"Error al probar la conexión: {e}")
        raise


def close_pool():
    """
    Cierra todas las conexiones del pool.
    
    Debe llamarse al finalizar la aplicación para liberar recursos.
    """
    global _connection_pool
    
    if _connection_pool:
        logger.info("Cerrando pool de conexiones...")
        _connection_pool.closeall()
        _connection_pool = None
        logger.info("Pool de conexiones cerrado")


def get_pool_status() -> Dict[str, Any]:
    """
    Obtiene información sobre el estado del pool de conexiones.
    
    Returns:
        dict: Información del pool
        
    Example:
        >>> status = get_pool_status()
        >>> print(f"Conexiones activas: {status['pool_size']}")
    """
    global _connection_pool
    
    if _connection_pool is None:
        return {
            'initialized': False,
            'pool_name': None,
            'pool_size': 0
        }
    
    config = DatabaseConfig.get_pool_config()
    return {
        'initialized': True,
        'pool_name': DatabaseConfig.POOL_NAME,
        'pool_size': config['maxconn']
    }


# ============================================
# INICIALIZACIÓN AUTOMÁTICA
# ============================================

# Inicializar el pool al importar el módulo
try:
    initialize_pool()
except OperationalError as e:
    logger.error(f"No se pudo inicializar el pool automáticamente: {e}")
    logger.warning("Las conexiones se crearán bajo demanda")