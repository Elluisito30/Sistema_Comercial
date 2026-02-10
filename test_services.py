"""
============================================
SCRIPT DE PRUEBA DE SERVICIOS
============================================
Prueba la lógica de negocio del sistema.
============================================
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).resolve().parent))

from services import ProductoService, CompraService, VentaService, InventarioService
from exceptions import *


def test_producto_service():
    """Prueba servicio de productos"""
    print("\n" + "="*60)
    print("PRUEBA: ProductoService")
    print("="*60)
    
    try:
        service = ProductoService()
        
        # Listar productos
        productos = service.listar_productos_activos()
        print(f"✓ Productos activos: {len(productos)}")
        
        # Buscar producto
        if productos:
            producto = service.obtener_producto_por_id(productos[0]['id'])
            print(f"✓ Producto obtenido: {producto['nombre']}")
        
        # Buscar por código
        try:
            producto_elec = service.obtener_producto_por_codigo('ELEC001')
            print(f"✓ Producto por código: {producto_elec['nombre']}")
        except ProductoNoEncontradoException as e:
            print(f"  ℹ {e.message}")
        
        # Productos con stock bajo
        stock_bajo = service.obtener_productos_stock_critico()
        print(f"✓ Productos con stock crítico: {len(stock_bajo)}")
        
        # Valor de inventario
        valor = service.calcular_valor_inventario()
        print(f"✓ Valor de inventario: S/. {valor['valor_venta']:.2f}")
        print(f"  - Ganancia potencial: S/. {valor['ganancia_potencial']:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_compra_service():
    """Prueba servicio de compras"""
    print("\n" + "="*60)
    print("PRUEBA: CompraService")
    print("="*60)
    
    try:
        service = CompraService()
        
        # Registrar una compra de prueba
        productos_compra = [
            {
                'producto_id': 1,  # Asumiendo que existe
                'cantidad': 10,
                'precio_unitario': 1800.00
            },
            {
                'producto_id': 2,
                'cantidad': 20,
                'precio_unitario': 25.00
            }
        ]
        
        print("Intentando registrar compra...")
        compra = service.registrar_compra(
            proveedor_id=1,  # Asumiendo que existe
            usuario_id=1,
            productos=productos_compra,
            observaciones="Compra de prueba desde test"
        )
        
        print(f"✓ Compra registrada: {compra['numero_compra']}")
        print(f"  - Total: S/. {compra['total']:.2f}")
        print(f"  - Productos: {compra['cantidad_productos']}")
        print(f"  - Estado: {compra['estado']}")
        
        # Listar compras pendientes
        pendientes = service.listar_compras(estado='pendiente')
        print(f"✓ Compras pendientes: {len(pendientes)}")
        
        # Recibir la compra
        if pendientes:
            compra_id = pendientes[0]['id']
            print(f"\nRecibiendo compra ID {compra_id}...")
            recibida = service.recibir_compra(compra_id, usuario_id=1)
            
            if recibida:
                print(f"✓ Compra recibida y stock actualizado")
        
        # Calcular totales del mes
        hoy = date.today()
        inicio_mes = date(hoy.year, hoy.month, 1)
        stats = service.calcular_total_compras_periodo(inicio_mes, hoy)
        print(f"\n✓ Estadísticas del mes:")
        print(f"  - Total compras: {stats['total_compras']}")
        print(f"  - Total gastado: S/. {stats['total_gastado']:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_venta_service():
    """Prueba servicio de ventas"""
    print("\n" + "="*60)
    print("PRUEBA: VentaService")
    print("="*60)
    
    try:
        service = VentaService()
        
        # Registrar una venta de prueba
        productos_venta = [
            {
                'producto_id': 1,  # Asumiendo que existe y tiene stock
                'cantidad': 2,
                'precio_unitario': 2500.00,
                'descuento': 0
            }
        ]
        
        print("Intentando registrar venta...")
        
        try:
            venta = service.registrar_venta(
                cliente_id=1,  # Asumiendo que existe
                usuario_id=1,
                productos=productos_venta,
                tipo_comprobante='boleta',
                metodo_pago='efectivo',
                observaciones="Venta de prueba desde test"
            )
            
            print(f"✓ Venta registrada: {venta['numero_venta']}")
            print(f"  - Total: S/. {venta['total']:.2f}")
            print(f"  - Cliente: {venta['cliente']}")
            print(f"  - Estado: {venta['estado']}")
            
        except StockInsuficienteException as e:
            print(f"  ℹ No se pudo registrar venta: {e.message}")
            print(f"    Stock disponible: {e.details['stock_disponible']}")
            print(f"    Cantidad solicitada: {e.details['cantidad_solicitada']}")
        
        # Listar ventas del día
        ventas_hoy = service.obtener_ventas_del_dia()
        print(f"\n✓ Ventas de hoy: {len(ventas_hoy)}")
        
        # Calcular totales del mes
        hoy = date.today()
        inicio_mes = date(hoy.year, hoy.month, 1)
        stats = service.calcular_total_ventas_periodo(inicio_mes, hoy)
        print(f"\n✓ Estadísticas del mes:")
        print(f"  - Total ventas: {stats['total_ventas']}")
        print(f"  - Total vendido: S/. {stats['total_vendido']:.2f}")
        print(f"  - Ticket promedio: S/. {stats['promedio_por_venta']:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_inventario_service():
    """Prueba servicio de inventario"""
    print("\n" + "="*60)
    print("PRUEBA: InventarioService")
    print("="*60)
    
    try:
        service = InventarioService()
        
        # Inventario actual
        inventario = service.obtener_inventario_actual()
        print(f"✓ Inventario actual: {len(inventario)} productos")
        
        # Productos con stock crítico
        criticos = service.obtener_productos_stock_critico()
        print(f"✓ Productos con stock crítico: {len(criticos)}")
        
        if criticos:
            for prod in criticos[:3]:
                print(f"  - {prod['nombre']}: Stock {prod['stock_actual']}/{prod['stock_minimo']}")
        
        # Valor total de inventario
        valor = service.calcular_valor_total_inventario()
        print(f"\n✓ Valor total de inventario:")
        print(f"  - Productos: {valor['total_productos']}")
        print(f"  - Unidades: {valor['total_unidades']}")
        print(f"  - Valor compra: S/. {valor['valor_compra']:.2f}")
        print(f"  - Valor venta: S/. {valor['valor_venta']:.2f}")
        print(f"  - Margen: {valor['margen_porcentaje']:.2f}%")
        
        # Historial de movimientos
        movimientos = service.obtener_historial_movimientos(limite=10)
        print(f"\n✓ Movimientos recientes: {len(movimientos)}")
        
        if movimientos:
            for mov in movimientos[:3]:
                print(f"  - {mov.get('producto_nombre', 'N/A')}: {mov['tipo_movimiento']} ({mov['cantidad']})")
        
        # Reporte de rotación
        rotacion = service.generar_reporte_rotacion(dias=30)
        print(f"\n✓ Reporte de rotación (30 días): {len(rotacion)} productos")
        
        if rotacion:
            print("  Top 5 productos más rotados:")
            for prod in rotacion[:5]:
                print(f"  - {prod['nombre']}: Rotación {prod['tasa_rotacion']}")
        
        # Productos sin movimiento
        sin_movimiento = service.obtener_productos_sin_movimiento(dias=60)
        print(f"\n✓ Productos sin movimiento (60 días): {len(sin_movimiento)}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "#"*60)
    print("# PRUEBAS DE SERVICIOS")
    print("#"*60)
    
    tests = [
        ("ProductoService", test_producto_service),
        ("CompraService", test_compra_service),
        ("VentaService", test_venta_service),
        ("InventarioService", test_inventario_service)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error inesperado en {name}: {e}")
            results.append((name, False))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nPruebas exitosas: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n✓ TODAS LAS PRUEBAS PASARON")
    else:
        print("\n✗ ALGUNAS PRUEBAS FALLARON")
    
    print("="*60)


if __name__ == '__main__':
    run_all_tests()