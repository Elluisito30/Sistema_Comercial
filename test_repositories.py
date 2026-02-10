"""
============================================
SCRIPT DE PRUEBA DE REPOSITORIOS
============================================
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent))

from repositories import (
    ProductoRepository,
    CategoriaRepository,
    ProveedorRepository,
    ClienteRepository,
    CompraRepository,
    VentaRepository,
    MovimientoRepository,
    UsuarioRepository
)


def test_categorias():
    """Prueba repositorio de categorías"""
    print("\n" + "="*60)
    print("PRUEBA: CategoriaRepository")
    print("="*60)
    
    try:
        repo = CategoriaRepository()
        
        # Obtener todas las categorías activas
        categorias = repo.get_all_active()
        print(f"✓ Categorías activas: {len(categorias)}")
        
        for cat in categorias[:3]:
            print(f"  - {cat['nombre']}")
        
        # Buscar por nombre
        categoria = repo.find_by_name('Electrónica')
        if categoria:
            print(f"✓ Categoría 'Electrónica' encontrada (ID: {categoria['id']})")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_productos():
    """Prueba repositorio de productos"""
    print("\n" + "="*60)
    print("PRUEBA: ProductoRepository")
    print("="*60)
    
    try:
        repo = ProductoRepository()
        
        # Obtener productos con categoría
        productos = repo.get_all_with_category()
        print(f"✓ Productos con categoría: {len(productos)}")
        
        for prod in productos[:3]:
            print(f"  - {prod['codigo']}: {prod['nombre']} (Stock: {prod['stock_actual']})")
        
        # Buscar por código
        producto = repo.find_by_codigo('ELEC001')
        if producto:
            print(f"✓ Producto ELEC001 encontrado: {producto['nombre']}")
        
        # Productos con stock bajo
        stock_bajo = repo.get_low_stock()
        print(f"✓ Productos con stock bajo: {len(stock_bajo)}")
        
        # Búsqueda
        resultados = repo.search('laptop')
        print(f"✓ Búsqueda 'laptop': {len(resultados)} resultados")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_proveedores():
    """Prueba repositorio de proveedores"""
    print("\n" + "="*60)
    print("PRUEBA: ProveedorRepository")
    print("="*60)
    
    try:
        repo = ProveedorRepository()
        
        proveedores = repo.get_all_active()
        print(f"✓ Proveedores activos: {len(proveedores)}")
        
        for prov in proveedores:
            print(f"  - {prov['razon_social']} (RUC: {prov['ruc']})")
        
        # Buscar por RUC
        proveedor = repo.find_by_ruc('20123456789')
        if proveedor:
            print(f"✓ Proveedor encontrado: {proveedor['razon_social']}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_clientes():
    """Prueba repositorio de clientes"""
    print("\n" + "="*60)
    print("PRUEBA: ClienteRepository")
    print("="*60)
    
    try:
        repo = ClienteRepository()
        
        clientes = repo.get_all_active()
        print(f"✓ Clientes activos: {len(clientes)}")
        
        for cliente in clientes[:3]:
            print(f"  - {cliente['nombres']} {cliente.get('apellidos', '')} ({cliente['numero_documento']})")
        
        # Buscar por documento
        cliente = repo.find_by_documento('12345678')
        if cliente:
            print(f"✓ Cliente encontrado: {cliente['nombres']}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_compras():
    """Prueba repositorio de compras"""
    print("\n" + "="*60)
    print("PRUEBA: CompraRepository")
    print("="*60)
    
    try:
        repo = CompraRepository()
        
        # Generar número de compra
        numero = repo.generate_numero_compra()
        print(f"✓ Número de compra generado: {numero}")
        
        # Obtener todas las compras
        compras = repo.get_all_with_details()
        print(f"✓ Total de compras: {len(compras)}")
        
        if compras:
            compra = compras[0]
            print(f"  - {compra['numero_compra']}: {compra.get('proveedor_nombre', 'N/A')} - S/. {compra['total']}")
            
            # Obtener detalle
            detalle = repo.get_detalle(compra['id'])
            print(f"  - Productos en esta compra: {len(detalle)}")
        
        # Compras por estado
        pendientes = repo.get_by_estado('pendiente')
        print(f"✓ Compras pendientes: {len(pendientes)}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_ventas():
    """Prueba repositorio de ventas"""
    print("\n" + "="*60)
    print("PRUEBA: VentaRepository")
    print("="*60)
    
    try:
        repo = VentaRepository()
        
        # Generar número de venta
        numero_boleta = repo.generate_numero_venta('boleta')
        numero_factura = repo.generate_numero_venta('factura')
        print(f"✓ Número de boleta generado: {numero_boleta}")
        print(f"✓ Número de factura generado: {numero_factura}")
        
        # Obtener ventas
        ventas = repo.get_all_with_details()
        print(f"✓ Total de ventas: {len(ventas)}")
        
        if ventas:
            venta = ventas[0]
            print(f"  - {venta['numero_venta']}: {venta.get('cliente_nombre', 'N/A')} - S/. {venta['total']}")
            
            # Obtener detalle
            detalle = repo.get_detalle(venta['id'])
            print(f"  - Productos en esta venta: {len(detalle)}")
        
        # Ventas del día
        hoy = date.today()
        ventas_hoy = repo.get_ventas_del_dia(hoy)
        print(f"✓ Ventas de hoy: {len(ventas_hoy)}")
        
        # Total vendido en el mes
        inicio_mes = date(hoy.year, hoy.month, 1)
        total_mes = repo.get_total_ventas_periodo(inicio_mes, hoy)
        print(f"✓ Total vendido en el mes: S/. {total_mes:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_movimientos():
    """Prueba repositorio de movimientos"""
    print("\n" + "="*60)
    print("PRUEBA: MovimientoRepository")
    print("="*60)
    
    try:
        repo = MovimientoRepository()
        
        # Movimientos recientes
        movimientos = repo.get_movimientos_recientes(10)
        print(f"✓ Movimientos recientes: {len(movimientos)}")
        
        for mov in movimientos[:5]:
            print(f"  - {mov.get('producto_nombre', 'N/A')}: {mov['tipo_movimiento']} ({mov['cantidad']} unidades)")
        
        # Movimientos por tipo
        entradas = repo.get_by_tipo('entrada')
        salidas = repo.get_by_tipo('salida')
        print(f"✓ Movimientos de entrada: {len(entradas)}")
        print(f"✓ Movimientos de salida: {len(salidas)}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_usuarios():
    """Prueba repositorio de usuarios"""
    print("\n" + "="*60)
    print("PRUEBA: UsuarioRepository")
    print("="*60)
    
    try:
        repo = UsuarioRepository()
        
        usuarios = repo.get_all_active()
        print(f"✓ Usuarios activos: {len(usuarios)}")
        
        for usuario in usuarios:
            print(f"  - {usuario['nombre_completo']} ({usuario['rol']})")
        
        # Buscar por username
        admin = repo.find_by_username('admin')
        if admin:
            print(f"✓ Usuario admin encontrado: {admin['nombre_completo']}")
        
        # Usuarios por rol
        vendedores = repo.get_by_rol('vendedor')
        print(f"✓ Vendedores: {len(vendedores)}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "#"*60)
    print("# PRUEBAS DE REPOSITORIOS")
    print("#"*60)
    
    tests = [
        ("Categorías", test_categorias),
        ("Productos", test_productos),
        ("Proveedores", test_proveedores),
        ("Clientes", test_clientes),
        ("Compras", test_compras),
        ("Ventas", test_ventas),
        ("Movimientos", test_movimientos),
        ("Usuarios", test_usuarios)
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