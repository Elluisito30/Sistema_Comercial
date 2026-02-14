"""
============================================
SCRIPT DE PRUEBA DE CONEXIÓN A POSTGRESQL
============================================
Valida que la configuración de base de datos sea correcta
y que se puedan realizar operaciones básicas.

Uso:
    python test_connection.py
============================================
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.database import (
    get_connection,
    get_db_connection,
    get_db_cursor,
    execute_query,
    test_connection,
    get_pool_status,
    close_pool
)
from config.settings import DatabaseConfig


def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "="*60)
    print(f"📌 {title}")
    print("="*60)


def print_success(message):
    print(f"   ✅ {message}")


def print_warning(message):
    print(f"   ⚠️  {message}")


def print_error(message):
    print(f"   ❌ {message}")


def test_1_basic_connection():
    """Prueba 1: Conexión básica y versión de PostgreSQL"""
    print_header("PRUEBA 1: Conexión Básica y Versión de PostgreSQL")
    
    start = time.time()
    try:
        # Probar conexión
        if not test_connection():
            print_error("No se pudo establecer conexión básica")
            return False
        
        # Obtener información detallada
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Versión de PostgreSQL
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            
            # Base de datos actual
            cursor.execute("SELECT current_database()")
            db_name = cursor.fetchone()[0]
            
            # Usuario actual
            cursor.execute("SELECT current_user")
            user = cursor.fetchone()[0]
            
            # Esquema actual
            cursor.execute("SELECT current_schema()")
            schema = cursor.fetchone()[0]
            
            cursor.close()
        
        elapsed = time.time() - start
        
        print_success(f"Conexión exitosa a PostgreSQL en {elapsed:.3f}s")
        print(f"   🗄️  Base de datos: {db_name}")
        print(f"   👤 Usuario: {user}")
        print(f"   📁 Esquema: {schema}")
        print(f"   🏷️  Versión: {version[:60]}...")
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_2_pool_status():
    """Prueba 2: Estado del pool de conexiones"""
    print_header("PRUEBA 2: Estado del Pool de Conexiones")
    
    try:
        status = get_pool_status()
        
        if not status['initialized']:
            print_warning("Pool no inicializado (se crearán conexiones bajo demanda)")
            return True
        
        print_success("Pool de conexiones inicializado correctamente")
        print(f"   🏊 Nombre: {status['pool_name']}")
        print(f"   📏 Tamaño máximo: {status['pool_size']} conexiones")
        print(f"   🗄️  Base de datos: {status['database']}")
        print(f"   🌐 Host: {status['host']}")
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_3_list_tables():
    """Prueba 3: Listar tablas del esquema público"""
    print_header("PRUEBA 3: Estructura de la Base de Datos")
    
    try:
        # Obtener tablas
        tablas = execute_query("""
            SELECT 
                table_name,
                table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        if not tablas:
            print_warning("No se encontraron tablas en el esquema 'public'")
            print_warning("  → Verifica que la base de datos tenga las tablas del sistema")
            return False
        
        print_success(f"Tablas encontradas: {len(tablas)}")
        
        # Agrupar por tipo
        tablas_sistema = [t for t in tablas if t['table_name'].startswith('pg_')]
        tablas_usuario = [t for t in tablas if not t['table_name'].startswith('pg_')]
        
        if tablas_usuario:
            print(f"\n   📋 Tablas del sistema ({len(tablas_usuario)}):")
            for i, tabla in enumerate(tablas_usuario[:15], 1):  # Mostrar primeras 15
                print(f"      {i}. {tabla['table_name']}")
            if len(tablas_usuario) > 15:
                print(f"      ... y {len(tablas_usuario) - 15} más")
        
        # Verificar tablas críticas
        tablas_criticas = ['usuarios', 'productos', 'categorias', 'clientes', 'ventas']
        faltantes = [t for t in tablas_criticas if not any(x['table_name'] == t for x in tablas_usuario)]
        
        if faltantes:
            print_error(f"⚠️  Tablas críticas faltantes: {', '.join(faltantes)}")
            return False
        
        print_success("✓ Todas las tablas críticas están presentes")
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_4_sample_queries():
    """Prueba 4: Consultas de muestra en tablas clave"""
    print_header("PRUEBA 4: Consultas en Tablas Clave")
    
    try:
        # Usuarios
        print("\n   👥 Usuarios:")
        usuarios = execute_query("SELECT id, nombre_usuario, rol, activo FROM usuarios ORDER BY id LIMIT 3")
        if usuarios:
            for u in usuarios:
                estado = "✅ Activo" if u['activo'] else "❌ Inactivo"
                print(f"      - [{u['id']}] {u['nombre_usuario']} ({u['rol']}) {estado}")
        else:
            print_warning("      No hay usuarios registrados (puede ser normal en BD nueva)")
        
        # Categorías
        print("\n   🗂️  Categorías:")
        categorias = execute_query("SELECT id, nombre, activo FROM categorias WHERE activo = TRUE ORDER BY nombre LIMIT 5")
        if categorias:
            for c in categorias:
                print(f"      - {c['nombre']}")
        else:
            print_warning("      No hay categorías activas")
        
        # Productos
        print("\n   📦 Productos:")
        productos = execute_query("""
            SELECT 
                codigo, 
                nombre, 
                precio_venta, 
                stock_actual,
                stock_minimo
            FROM productos 
            WHERE activo = TRUE 
            ORDER BY nombre 
            LIMIT 5
        """)
        if productos:
            for p in productos:
                stock_status = "⚠️ Bajo" if p['stock_actual'] <= p['stock_minimo'] else "✅ Normal"
                print(f"      - {p['codigo']}: {p['nombre'][:30]:30s} | S/. {p['precio_venta']:7.2f} | Stock: {p['stock_actual']:3d} ({stock_status})")
        else:
            print_warning("      No hay productos activos")
        
        print_success("Consultas ejecutadas correctamente")
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_5_transaction():
    """Prueba 5: Transacciones ACID - Compatible 100% con PostgreSQL"""
    print_header("PRUEBA 5: Transacciones ACID")
    
    try:
        # Usar SAVEPOINT para prueba segura sin afectar datos reales
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Crear savepoint
            cursor.execute("SAVEPOINT test_transaccion_safe")
            
            # Obtener un producto con stock
            cursor.execute("""
                SELECT id, stock_actual 
                FROM productos 
                WHERE activo = TRUE AND stock_actual > 0
                ORDER BY id 
                LIMIT 1
            """)
            producto = cursor.fetchone()
            
            if not producto:
                print_warning("⚠️  No hay productos con stock para probar transacciones")
                cursor.execute("ROLLBACK TO SAVEPOINT test_transaccion_safe")
                cursor.execute("RELEASE SAVEPOINT test_transaccion_safe")
                return True
            
            producto_id = producto[0]
            stock_original = producto[1]
            
            # Simular actualización dentro de transacción
            cursor.execute(
                "UPDATE productos SET stock_actual = stock_actual - 1 WHERE id = %s",
                (producto_id,)
            )
            
            # Verificar cambio temporal
            cursor.execute(
                "SELECT stock_actual FROM productos WHERE id = %s",
                (producto_id,)
            )
            stock_temporal = cursor.fetchone()[0]
            
            # Revertir solo esta operación con ROLLBACK TO SAVEPOINT
            cursor.execute("ROLLBACK TO SAVEPOINT test_transaccion_safe")
            
            # Verificar que el stock volvió a original
            cursor.execute(
                "SELECT stock_actual FROM productos WHERE id = %s",
                (producto_id,)
            )
            stock_final = cursor.fetchone()[0]
            
            # Liberar savepoint
            cursor.execute("RELEASE SAVEPOINT test_transaccion_safe")
            
            if stock_final == stock_original:
                print_success("Transacciones ACID funcionando correctamente")
                print(f"   ✅ Savepoint/rollback exitoso: {stock_original} → {stock_temporal} → {stock_final}")
                return True
            else:
                print_error(f"✗ Rollback fallido: Stock original {stock_original}, final {stock_final}")
                return False
                
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_6_views_and_functions():
    """Prueba 6: Vistas y funciones del sistema"""
    print_header("PRUEBA 6: Vistas y Funciones")
    
    vistas_esperadas = [
        'v_productos_stock_bajo',
        'v_inventario_valorizado',
        'v_ventas_diarias'
    ]
    
    try:
        # Verificar vistas
        vistas_existentes = execute_query("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        vistas_encontradas = [v['table_name'] for v in vistas_existentes]
        
        print(f"   📊 Vistas encontradas: {len(vistas_encontradas)}")
        
        for vista in vistas_esperadas:
            if vista in vistas_encontradas:
                print_success(f"   ✓ Vista '{vista}' existe")
            else:
                print_warning(f"   ⚠️  Vista '{vista}' no encontrada (opcional)")
        
        # Probar una vista
        if 'v_productos_stock_bajo' in vistas_encontradas:
            stock_bajo = execute_query("SELECT COUNT(*) as total FROM v_productos_stock_bajo")
            print(f"   📉 Productos con stock bajo: {stock_bajo[0]['total']}")
        
        return True
        
    except Exception as e:
        print_warning(f"No se pudieron verificar vistas: {str(e)}")
        return True  # No es crítico


def run_all_tests():
    """Ejecuta todas las pruebas y muestra resumen"""
    
    print("\n" + "#"*60)
    print("#" + " "*16 + "PRUEBAS DE POSTGRESQL" + " "*16 + "#")
    print("#"*60)
    print(f"\n📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⚙️  Configuración:")
    print(f"   Host: {DatabaseConfig.HOST}")
    print(f"   Puerto: {DatabaseConfig.PORT}")
    print(f"   Base de datos: {DatabaseConfig.NAME}")
    print(f"   Usuario: {DatabaseConfig.USER}")
    
    tests = [
        ("Conexión Básica", test_1_basic_connection),
        ("Pool de Conexiones", test_2_pool_status),
        ("Estructura de BD", test_3_list_tables),
        ("Consultas en Tablas", test_4_sample_queries),
        ("Transacciones ACID", test_5_transaction),
        ("Vistas y Funciones", test_6_views_and_functions)
    ]
    
    results = []
    start_total = time.time()
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Excepción inesperada en '{name}': {str(e)}")
            results.append((name, False))
    
    elapsed_total = time.time() - start_total
    
    # Resumen final
    print_header("RESUMEN FINAL")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n✅ Pruebas exitosas: {passed}/{total}")
    print(f"⏱️  Tiempo total: {elapsed_total:.2f} segundos")
    
    if passed == total:
        print("\n" + "🎉"*20)
        print("   ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        print("   Tu configuración de PostgreSQL está CORRECTA.")
        print("🎉"*20)
        return True
    else:
        print("\n" + "⚠️ "*20)
        print("   ALGUNAS PRUEBAS FALLARON")
        print("   Revisa los errores reportados arriba.")
        print("⚠️ "*20)
        
        # Mostrar pruebas fallidas
        fallidas = [name for name, result in results if not result]
        if fallidas:
            print("\n   Pruebas fallidas:")
            for name in fallidas:
                print(f"      ❌ {name}")
        return False


if __name__ == '__main__':
    try:
        exit_code = 0 if run_all_tests() else 1
        
        # Cerrar pool al finalizar
        print("\n" + "="*60)
        print("Cerrando pool de conexiones...")
        close_pool()
        print("Pool cerrado correctamente.")
        print("="*60)
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")
        close_pool()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")
        close_pool()
        sys.exit(1)