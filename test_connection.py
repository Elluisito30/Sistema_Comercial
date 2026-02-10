"""
============================================
SCRIPT DE PRUEBA DE CONEXIÓN A BASE DE DATOS
============================================
Valida que la configuración de base de datos sea correcta
y que se puedan realizar operaciones básicas.

Uso:
    python test_connection.py
============================================
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.database import (
    get_connection,
    get_db_connection,
    get_db_cursor,
    execute_query,
    test_connection,
    get_pool_status
)
from config.settings import DatabaseConfig


def test_basic_connection():
    """Prueba 1: Conexión básica"""
    print("\n" + "="*50)
    print("PRUEBA 1: Conexión Básica")
    print("="*50)
    
    try:
        test_connection()
        print("✓ Conexión exitosa")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_pool_status():
    """Prueba 2: Estado del pool"""
    print("\n" + "="*50)
    print("PRUEBA 2: Estado del Pool de Conexiones")
    print("="*50)
    
    try:
        status = get_pool_status()
        print(f"Pool inicializado: {status['initialized']}")
        print(f"Nombre del pool: {status['pool_name']}")
        print(f"Tamaño del pool: {status['pool_size']}")
        print(f"Base de datos: {status['database']}")
        print(f"Host: {status['host']}")
        print("✓ Pool funcionando correctamente")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_simple_query():
    """Prueba 3: Consulta simple"""
    print("\n" + "="*50)
    print("PRUEBA 3: Consulta Simple")
    print("="*50)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            result = cursor.fetchone()
            cursor.close()
            
            print(f"Total de usuarios: {result['total']}")
            print("✓ Consulta ejecutada correctamente")
            return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_context_manager():
    """Prueba 4: Context manager con cursor"""
    print("\n" + "="*50)
    print("PRUEBA 4: Context Manager con Cursor")
    print("="*50)
    
    try:
        with get_db_cursor() as (cursor, conn):
            cursor.execute("SELECT * FROM categorias WHERE activo = TRUE")
            categorias = cursor.fetchall()
            
            print(f"Total de categorías activas: {len(categorias)}")
            for cat in categorias:
                print(f"  - {cat['nombre']}")
            
            print("✓ Context manager funcionando correctamente")
            return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_execute_query():
    """Prueba 5: Función execute_query"""
    print("\n" + "="*50)
    print("PRUEBA 5: Función execute_query")
    print("="*50)
    
    try:
        # Consulta con fetchall
        productos = execute_query(
            "SELECT codigo, nombre, precio_venta, stock_actual FROM productos LIMIT 5"
        )
        
        print(f"Productos encontrados: {len(productos)}")
        for prod in productos:
            print(f"  - {prod['codigo']}: {prod['nombre']} - Stock: {prod['stock_actual']}")
        
        # Consulta con fetchone
        usuario = execute_query(
            "SELECT nombre_usuario, nombre_completo, rol FROM usuarios WHERE id = %s",
            (1,),
            fetch='one'
        )
        
        if usuario:
            print(f"\nUsuario admin:")
            print(f"  Usuario: {usuario['nombre_usuario']}")
            print(f"  Nombre: {usuario['nombre_completo']}")
            print(f"  Rol: {usuario['rol']}")
        
        print("✓ execute_query funcionando correctamente")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_views():
    """Prueba 6: Consultar vistas"""
    print("\n" + "="*50)
    print("PRUEBA 6: Consultar Vistas")
    print("="*50)
    
    try:
        # Vista de productos con stock bajo
        stock_bajo = execute_query("SELECT * FROM v_productos_stock_bajo LIMIT 5")
        
        if stock_bajo:
            print(f"Productos con stock bajo: {len(stock_bajo)}")
            for prod in stock_bajo:
                print(f"  - {prod['nombre']}: Stock {prod['stock_actual']}/{prod['stock_minimo']}")
        else:
            print("No hay productos con stock bajo (¡Excelente!)")
        
        # Vista de inventario valorizado
        inventario = execute_query(
            "SELECT * FROM v_inventario_valorizado ORDER BY valor_inventario_venta DESC LIMIT 3"
        )
        
        print(f"\nTop 3 productos por valor en inventario:")
        for prod in inventario:
            print(f"  - {prod['nombre']}: S/. {prod['valor_inventario_venta']:.2f}")
        
        print("✓ Vistas funcionando correctamente")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "#"*50)
    print("# PRUEBAS DE CONEXIÓN A BASE DE DATOS")
    print("#"*50)
    
    tests = [
        test_basic_connection,
        test_pool_status,
        test_simple_query,
        test_context_manager,
        test_execute_query,
        test_views
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Error inesperado en {test.__name__}: {e}")
            results.append(False)
    
    # Resumen
    print("\n" + "="*50)
    print("RESUMEN DE PRUEBAS")
    print("="*50)
    passed = sum(results)
    total = len(results)
    print(f"Pruebas exitosas: {passed}/{total}")
    
    if passed == total:
        print("\n✓ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("La configuración de base de datos está correcta.")
    else:
        print("\n✗ ALGUNAS PRUEBAS FALLARON")
        print("Revisa la configuración en el archivo .env")
    
    print("="*50)


if __name__ == '__main__':
    run_all_tests()