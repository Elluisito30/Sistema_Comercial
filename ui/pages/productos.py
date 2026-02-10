"""
============================================
PRODUCTOS - GESTIÓN DE CATÁLOGO
============================================
CRUD completo de productos
"""

import streamlit as st
from services import ProductoService
from repositories import CategoriaRepository
from exceptions import ProductoNoEncontradoException, DatosInvalidosException
import pandas as pd

def render():
    """Renderiza la página de productos"""
    
    st.markdown("<h1 class='main-header'>📦 Gestión de Productos</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Pestañas
    tab1, tab2, tab3 = st.tabs(["📋 Listar Productos", "➕ Crear Producto", "✏️ Editar Producto"])
    
    # ============================================
    # TAB 1: LISTAR PRODUCTOS
    # ============================================
    
    with tab1:
        listar_productos()
    
    # ============================================
    # TAB 2: CREAR PRODUCTO
    # ============================================
    
    with tab2:
        crear_producto()
    
    # ============================================
    # TAB 3: EDITAR PRODUCTO
    # ============================================
    
    with tab3:
        editar_producto()


def listar_productos():
    """Lista todos los productos activos"""
    
    st.subheader("📋 Lista de Productos")
    
    try:
        producto_service = ProductoService()
        
        # Filtros
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            termino_busqueda = st.text_input(
                "🔍 Buscar",
                placeholder="Código o nombre del producto...",
                key="buscar_producto"
            )
        
        with col2:
            categoria_repo = CategoriaRepository()
            categorias = categoria_repo.get_all_active()
            categoria_filtro = st.selectbox(
                "Categoría",
                options=["Todas"] + [cat['nombre'] for cat in categorias],
                key="filtro_categoria"
            )
        
        with col3:
            st.write("")  # Espaciado
            st.write("")
            mostrar_inactivos = st.checkbox("Ver inactivos", value=False)
        
        # Obtener productos
        if termino_busqueda:
            productos = producto_service.buscar_productos(termino_busqueda)
        else:
            productos = producto_service.listar_productos_activos()
        
        # Filtrar por categoría
        if categoria_filtro != "Todas":
            productos = [p for p in productos if p.get('categoria_nombre') == categoria_filtro]
        
        # Mostrar total
        st.info(f"📊 Total de productos: **{len(productos)}**")
        
        if productos:
            # Convertir a DataFrame para mejor visualización
            df = pd.DataFrame(productos)
            
            # Seleccionar columnas a mostrar
            columnas_mostrar = [
                'codigo', 'nombre', 'categoria_nombre', 
                'precio_compra', 'precio_venta', 'stock_actual', 'stock_minimo'
            ]
            
            # Renombrar columnas
            df_display = df[columnas_mostrar].copy()
            df_display.columns = [
                'Código', 'Nombre', 'Categoría', 
                'P. Compra', 'P. Venta', 'Stock', 'Stock Mín.'
            ]
            
            # Formatear precios
            df_display['P. Compra'] = df_display['P. Compra'].apply(lambda x: f"S/. {x:.2f}")
            df_display['P. Venta'] = df_display['P. Venta'].apply(lambda x: f"S/. {x:.2f}")
            
            # Aplicar colores según stock
            def highlight_stock(row):
                if row['Stock'] <= row['Stock Mín.']:
                    return ['background-color: #ffcccc'] * len(row)
                return [''] * len(row)
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True
            )
            
            # Botón para exportar
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name="productos.csv",
                mime="text/csv"
            )
            
        else:
            st.warning("No se encontraron productos")
    
    except Exception as e:
        st.error(f"Error cargando productos: {str(e)}")


def crear_producto():
    """Formulario para crear un nuevo producto"""
    
    st.subheader("➕ Crear Nuevo Producto")
    
    try:
        with st.form("form_crear_producto", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                codigo = st.text_input("Código *", placeholder="PROD001")
                nombre = st.text_input("Nombre *", placeholder="Nombre del producto")
                
                categoria_repo = CategoriaRepository()
                categorias = categoria_repo.get_all_active()
                categoria_id = st.selectbox(
                    "Categoría *",
                    options=[cat['id'] for cat in categorias],
                    format_func=lambda x: next(cat['nombre'] for cat in categorias if cat['id'] == x)
                )
                
                descripcion = st.text_area("Descripción", placeholder="Descripción del producto")
            
            with col2:
                precio_compra = st.number_input(
                    "Precio de Compra (S/.) *",
                    min_value=0.01,
                    value=10.0,
                    step=0.01,
                    format="%.2f"
                )
                
                precio_venta = st.number_input(
                    "Precio de Venta (S/.) *",
                    min_value=0.01,
                    value=15.0,
                    step=0.01,
                    format="%.2f"
                )
                
                stock_minimo = st.number_input(
                    "Stock Mínimo *",
                    min_value=0,
                    value=5,
                    step=1
                )
                
                unidad_medida = st.selectbox(
                    "Unidad de Medida *",
                    options=["unidad", "caja", "par", "bolsa", "kg", "litro", "metro"]
                )
            
            submitted = st.form_submit_button("✅ Crear Producto", use_container_width=True)
            
            if submitted:
                # Validar campos requeridos
                if not codigo or not nombre:
                    st.error("⚠️ Código y nombre son obligatorios")
                    return
                
                if precio_venta < precio_compra:
                    st.warning("⚠️ El precio de venta es menor al precio de compra")
                
                try:
                    producto_service = ProductoService()
                    
                    # Verificar si el código ya existe
                    try:
                        producto_existente = producto_service.obtener_producto_por_codigo(codigo)
                        if producto_existente:
                            st.error(f"⚠️ Ya existe un producto con el código '{codigo}'")
                            return
                    except ProductoNoEncontradoException:
                        pass  # El código no existe, podemos continuar
                    
                    # Crear el producto
                    nuevo_producto = producto_service.crear_producto(
                        codigo=codigo,
                        nombre=nombre,
                        descripcion=descripcion,
                        categoria_id=categoria_id,
                        precio_compra=precio_compra,
                        precio_venta=precio_venta,
                        stock_minimo=stock_minimo,
                        unidad_medida=unidad_medida
                    )
                    
                    st.success(f"✅ Producto '{nombre}' creado exitosamente (ID: {nuevo_producto['id']})")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Error creando producto: {str(e)}")
    
    except Exception as e:
        st.error(f"Error en el formulario: {str(e)}")


def editar_producto():
    """Formulario para editar un producto existente"""
    
    st.subheader("✏️ Editar Producto")
    
    try:
        producto_service = ProductoService()
        productos = producto_service.listar_productos_activos()
        
        if not productos:
            st.warning("No hay productos para editar")
            return
        
        # Selector de producto
        producto_seleccionado = st.selectbox(
            "Seleccionar Producto",
            options=productos,
            format_func=lambda x: f"{x['codigo']} - {x['nombre']}",
            key="producto_editar"
        )
        
        if producto_seleccionado:
            st.markdown("---")
            
            with st.form("form_editar_producto"):
                col1, col2 = st.columns(2)
                
                with col1:
                    codigo = st.text_input("Código", value=producto_seleccionado['codigo'], disabled=True)
                    nombre = st.text_input("Nombre *", value=producto_seleccionado['nombre'])
                    
                    categoria_repo = CategoriaRepository()
                    categorias = categoria_repo.get_all_active()
                    
                    categoria_idx = next(
                        (i for i, cat in enumerate(categorias) if cat['id'] == producto_seleccionado['categoria_id']),
                        0
                    )
                    
                    categoria_id = st.selectbox(
                        "Categoría *",
                        options=[cat['id'] for cat in categorias],
                        format_func=lambda x: next(cat['nombre'] for cat in categorias if cat['id'] == x),
                        index=categoria_idx
                    )
                    
                    descripcion = st.text_area(
                        "Descripción",
                        value=producto_seleccionado.get('descripcion', '')
                    )
                
                with col2:
                    precio_compra = st.number_input(
                        "Precio de Compra (S/.) *",
                        min_value=0.01,
                        value=float(producto_seleccionado['precio_compra']),
                        step=0.01,
                        format="%.2f"
                    )
                    
                    precio_venta = st.number_input(
                        "Precio de Venta (S/.) *",
                        min_value=0.01,
                        value=float(producto_seleccionado['precio_venta']),
                        step=0.01,
                        format="%.2f"
                    )
                    
                    stock_minimo = st.number_input(
                        "Stock Mínimo *",
                        min_value=0,
                        value=producto_seleccionado['stock_minimo'],
                        step=1
                    )
                    
                    unidad_medida = st.selectbox(
                        "Unidad de Medida *",
                        options=["unidad", "caja", "par", "bolsa", "kg", "litro", "metro"],
                        index=["unidad", "caja", "par", "bolsa", "kg", "litro", "metro"].index(
                            producto_seleccionado['unidad_medida']
                        ) if producto_seleccionado['unidad_medida'] in ["unidad", "caja", "par", "bolsa", "kg", "litro", "metro"] else 0
                    )
                    
                    activo = st.checkbox("Producto Activo", value=producto_seleccionado.get('activo', True))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    submitted = st.form_submit_button("💾 Guardar Cambios", use_container_width=True)
                
                with col2:
                    desactivar = st.form_submit_button("🗑️ Desactivar Producto", use_container_width=True)
                
                if submitted:
                    try:
                        producto_service.actualizar_producto(
                            producto_id=producto_seleccionado['id'],
                            nombre=nombre,
                            descripcion=descripcion,
                            categoria_id=categoria_id,
                            precio_compra=precio_compra,
                            precio_venta=precio_venta,
                            stock_minimo=stock_minimo,
                            unidad_medida=unidad_medida,
                            activo=activo
                        )
                        
                        st.success("✅ Producto actualizado exitosamente")
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error actualizando producto: {str(e)}")
                
                if desactivar:
                    try:
                        producto_service.desactivar_producto(producto_seleccionado['id'])
                        st.success("✅ Producto desactivado exitosamente")
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error desactivando producto: {str(e)}")
    
    except Exception as e:
        st.error(f"Error en el formulario de edición: {str(e)}")
