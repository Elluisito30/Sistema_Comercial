"""
============================================
INVENTARIO - CONSULTA Y CONTROL
============================================
Consulta general de inventario y productos con stock crítico
"""

import streamlit as st
from services import InventarioService, ProductoService
from exceptions import *
from datetime import datetime, date, timedelta
import pandas as pd

def render():
    """Renderiza la página de inventario"""
    
    st.markdown("<h1 class='main-header'>📊 Gestión de Inventario</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Pestañas
    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Inventario General",
        "⚠️ Stock Crítico",
        "🔧 Ajustes",
        "📜 Historial"
    ])
    
    with tab1:
        inventario_general()
    
    with tab2:
        stock_critico()
    
    with tab3:
        ajustes_inventario()
    
    with tab4:
        historial_movimientos()


def inventario_general():
    """Muestra el inventario general"""
    
    st.subheader("📦 Inventario General")
    
    try:
        inventario_service = InventarioService()
        
        # Obtener inventario
        productos = inventario_service.obtener_inventario_actual()
        
        if not productos:
            st.warning("No hay productos en el inventario")
            return
        
        # Calcular métricas
        valor_inventario = inventario_service.calcular_valor_total_inventario()
        
        # Mostrar métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Productos",
                valor_inventario['total_productos']
            )
        
        with col2:
            st.metric(
                "Total Unidades",
                f"{valor_inventario['total_unidades']:,}"
            )
        
        with col3:
            st.metric(
                "Valor Inventario",
                f"S/. {valor_inventario['valor_venta']:,.2f}"
            )
        
        with col4:
            st.metric(
                "Margen Promedio",
                f"{valor_inventario['margen_porcentaje']:.1f}%"
            )
        
        st.markdown("---")
        
        # Filtros
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            termino_busqueda = st.text_input(
                "🔍 Buscar",
                placeholder="Código o nombre del producto...",
                key="buscar_inventario"
            )
        
        with col2:
            from repositories import CategoriaRepository
            categoria_repo = CategoriaRepository()
            categorias = categoria_repo.get_all_active()
            categoria_filtro = st.selectbox(
                "Categoría",
                options=["Todas"] + [cat['nombre'] for cat in categorias],
                key="filtro_categoria_inv"
            )
        
        with col3:
            orden = st.selectbox(
                "Ordenar por",
                options=["Nombre", "Stock", "Valor"],
                key="orden_inventario"
            )
        
        # Filtrar productos
        productos_filtrados = productos.copy()
        
        if termino_busqueda:
            productos_filtrados = [
                p for p in productos_filtrados
                if termino_busqueda.lower() in p['codigo'].lower()
                or termino_busqueda.lower() in p['nombre'].lower()
            ]
        
        if categoria_filtro != "Todas":
            productos_filtrados = [
                p for p in productos_filtrados
                if p.get('categoria_nombre') == categoria_filtro
            ]
        
        # Ordenar
        if orden == "Stock":
            productos_filtrados.sort(key=lambda x: x['stock_actual'])
        elif orden == "Valor":
            productos_filtrados.sort(
                key=lambda x: x['stock_actual'] * x['precio_venta'],
                reverse=True
            )
        else:  # Nombre
            productos_filtrados.sort(key=lambda x: x['nombre'])
        
        st.info(f"📊 Mostrando {len(productos_filtrados)} productos")
        
        # Mostrar productos
        if productos_filtrados:
            # Crear DataFrame
            df = pd.DataFrame(productos_filtrados)
            
            # Añadir columnas calculadas
            df['Valor Stock'] = df['stock_actual'] * df['precio_venta']
            df['% Stock'] = ((df['stock_actual'] / df['stock_minimo'] * 100)
                           .apply(lambda x: f"{x:.0f}%"))
            
            # Seleccionar y renombrar columnas
            df_display = df[[
                'codigo', 'nombre', 'categoria_nombre',
                'stock_actual', 'stock_minimo',
                'precio_compra', 'precio_venta',
                'Valor Stock', '% Stock'
            ]].copy()
            
            df_display.columns = [
                'Código', 'Producto', 'Categoría',
                'Stock', 'Stock Mín.',
                'P. Compra', 'P. Venta',
                'Valor Stock', '% Stock'
            ]
            
            # Formatear valores
            df_display['P. Compra'] = df_display['P. Compra'].apply(lambda x: f"S/. {x:.2f}")
            df_display['P. Venta'] = df_display['P. Venta'].apply(lambda x: f"S/. {x:.2f}")
            df_display['Valor Stock'] = df_display['Valor Stock'].apply(lambda x: f"S/. {x:.2f}")
            
            # Aplicar estilos según stock
            def resaltar_stock_bajo(row):
                if row['Stock'] <= row['Stock Mín.']:
                    return ['background-color: #ffcccc'] * len(row)
                return [''] * len(row)
            
            # Mostrar tabla
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Botón exportar
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar a CSV",
                data=csv,
                file_name=f"inventario_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        else:
            st.warning("No se encontraron productos con los filtros aplicados")
    
    except Exception as e:
        st.error(f"Error cargando inventario: {str(e)}")


def stock_critico():
    """Muestra productos con stock crítico"""
    
    st.subheader("⚠️ Productos con Stock Crítico")
    
    try:
        producto_service = ProductoService()
        
        # Obtener productos con stock crítico
        productos_criticos = producto_service.obtener_productos_stock_critico()
        
        if not productos_criticos:
            st.success("✅ Todos los productos tienen stock suficiente")
            return
        
        st.error(f"⚠️ **{len(productos_criticos)} productos** requieren reabastecimiento")
        
        # Mostrar productos críticos
        for producto in productos_criticos:
            with st.expander(
                f"🔴 {producto['codigo']} - {producto['nombre']} "
                f"(Stock: {producto['stock_actual']} / Mín: {producto['stock_minimo']})"
            ):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Categoría:** {producto.get('categoria_nombre', 'N/A')}")
                    st.write(f"**Stock Actual:** {producto['stock_actual']}")
                    st.write(f"**Stock Mínimo:** {producto['stock_minimo']}")
                
                with col2:
                    faltante = producto['stock_minimo'] - producto['stock_actual']
                    st.write(f"**Unidades Faltantes:** {faltante}")
                    st.write(f"**Precio Compra:** S/. {producto['precio_compra']:.2f}")
                    st.write(f"**Inversión Requerida:** S/. {faltante * producto['precio_compra']:.2f}")
                
                with col3:
                    st.write(f"**Precio Venta:** S/. {producto['precio_venta']:.2f}")
                    st.write(f"**Unidad:** {producto['unidad_medida']}")
                    
                    # Calcular días de stock (estimado)
                    if producto['stock_actual'] > 0:
                        st.write(f"**Estado:** 🔴 Crítico")
                    else:
                        st.write(f"**Estado:** ⚫ Sin Stock")
                
                # Botón para generar orden de compra
                if st.button(
                    "📝 Generar Orden de Compra",
                    key=f"orden_{producto['id']}"
                ):
                    st.info("Funcionalidad disponible en el módulo de Compras")
        
        # Resumen de reabastecimiento
        st.markdown("---")
        st.subheader("💰 Resumen de Reabastecimiento")
        
        total_unidades = sum(
            max(0, p['stock_minimo'] - p['stock_actual'])
            for p in productos_criticos
        )
        
        inversion_total = sum(
            max(0, p['stock_minimo'] - p['stock_actual']) * p['precio_compra']
            for p in productos_criticos
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Productos Afectados", len(productos_criticos))
        
        with col2:
            st.metric("Unidades a Comprar", f"{total_unidades:,}")
        
        with col3:
            st.metric("Inversión Estimada", f"S/. {inversion_total:,.2f}")
    
    except Exception as e:
        st.error(f"Error cargando stock crítico: {str(e)}")


def ajustes_inventario():
    """Formulario para realizar ajustes manuales de inventario"""
    
    st.subheader("🔧 Ajustes de Inventario")
    
    st.warning("⚠️ Los ajustes de inventario modifican directamente el stock. Use con precaución.")
    
    try:
        producto_service = ProductoService()
        inventario_service = InventarioService()
        
        productos = producto_service.listar_productos_activos()
        
        if not productos:
            st.error("No hay productos disponibles")
            return
        
        with st.form("form_ajuste_inventario"):
            # Seleccionar producto
            producto_seleccionado = st.selectbox(
                "Producto *",
                options=productos,
                format_func=lambda x: f"{x['codigo']} - {x['nombre']} (Stock actual: {x['stock_actual']})",
                key="producto_ajuste"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Stock Actual:** {producto_seleccionado['stock_actual']} {producto_seleccionado['unidad_medida']}")
                
                nuevo_stock = st.number_input(
                    "Nuevo Stock *",
                    min_value=0,
                    value=producto_seleccionado['stock_actual'],
                    step=1,
                    key="nuevo_stock"
                )
                
                diferencia = nuevo_stock - producto_seleccionado['stock_actual']
                
                if diferencia > 0:
                    st.success(f"➕ Incremento: {diferencia} unidades")
                elif diferencia < 0:
                    st.error(f"➖ Reducción: {abs(diferencia)} unidades")
                else:
                    st.info("Sin cambios")
            
            with col2:
                motivo = st.selectbox(
                    "Motivo del Ajuste *",
                    options=[
                        "inventario_físico",
                        "merma",
                        "robo",
                        "daño",
                        "corrección",
                        "otro"
                    ],
                    format_func=lambda x: {
                        "inventario_físico": "Inventario Físico",
                        "merma": "Merma",
                        "robo": "Robo/Pérdida",
                        "daño": "Daño/Deterioro",
                        "corrección": "Corrección de Error",
                        "otro": "Otro"
                    }[x],
                    key="motivo_ajuste"
                )
                
                observaciones = st.text_area(
                    "Observaciones *",
                    placeholder="Describa el motivo del ajuste...",
                    key="obs_ajuste"
                )
            
            submitted = st.form_submit_button(
                "✅ Aplicar Ajuste",
                type="primary",
                use_container_width=True
            )
            
            if submitted:
                if not observaciones:
                    st.error("⚠️ Las observaciones son obligatorias")
                    return
                
                if diferencia == 0:
                    st.warning("⚠️ No hay cambios en el stock")
                    return
                
                try:
                    # Confirmar ajuste
                    st.warning(f"⚠️ Está a punto de ajustar el stock de **{producto_seleccionado['nombre']}** "
                             f"de **{producto_seleccionado['stock_actual']}** a **{nuevo_stock}**")
                    
                    # Realizar ajuste
                    inventario_service.ajustar_inventario(
                        producto_id=producto_seleccionado['id'],
                        nuevo_stock=nuevo_stock,
                        motivo=motivo,
                        usuario_id=st.session_state.usuario_id,
                        observaciones=observaciones
                    )
                    
                    st.success("✅ Ajuste de inventario realizado exitosamente")
                    st.balloons()
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error realizando ajuste: {str(e)}")
    
    except Exception as e:
        st.error(f"Error en el formulario de ajuste: {str(e)}")


def historial_movimientos():
    """Muestra el historial de movimientos de inventario"""
    
    st.subheader("📜 Historial de Movimientos")
    
    try:
        inventario_service = InventarioService()
        
        # Filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            tipo_movimiento = st.selectbox(
                "Tipo de Movimiento",
                options=["Todos", "entrada", "salida", "ajuste"],
                key="filtro_tipo_mov"
            )
        
        with col2:
            fecha_inicio = st.date_input(
                "Fecha Inicio",
                value=date.today() - timedelta(days=30),
                key="fecha_inicio_mov"
            )
        
        with col3:
            fecha_fin = st.date_input(
                "Fecha Fin",
                value=date.today(),
                key="fecha_fin_mov"
            )
        
        with col4:
            limite = st.number_input(
                "Límite",
                min_value=10,
                max_value=500,
                value=50,
                step=10,
                key="limite_mov"
            )
        
        # Obtener movimientos
        if tipo_movimiento == "Todos":
            movimientos = inventario_service.obtener_historial_movimientos(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                limite=limite
            )
        else:
            movimientos = inventario_service.obtener_historial_movimientos(
                tipo_movimiento=tipo_movimiento,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                limite=limite
            )
        
        if movimientos:
            st.info(f"📊 Total de movimientos: **{len(movimientos)}**")
            
            # Mostrar movimientos
            for mov in movimientos:
                tipo_emoji = {
                    'entrada': '📥',
                    'salida': '📤',
                    'ajuste': '🔧'
                }
                
                tipo_color = {
                    'entrada': 'green',
                    'salida': 'red',
                    'ajuste': 'orange'
                }
                
                with st.expander(
                    f"{tipo_emoji.get(mov['tipo_movimiento'], '📄')} "
                    f"{mov.get('producto_nombre', 'N/A')} - "
                    f"{mov['tipo_movimiento'].upper()} - "
                    f"{mov['cantidad']} unidades - "
                    f"{mov['fecha_movimiento']}"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Producto:** {mov.get('producto_nombre', 'N/A')}")
                        st.write(f"**Tipo:** {mov['tipo_movimiento'].upper()}")
                        st.write(f"**Cantidad:** {mov['cantidad']}")
                        st.write(f"**Motivo:** {mov['motivo']}")
                    
                    with col2:
                        st.write(f"**Stock Anterior:** {mov['stock_anterior']}")
                        st.write(f"**Stock Nuevo:** {mov['stock_nuevo']}")
                        st.write(f"**Usuario:** {mov.get('usuario_nombre', 'N/A')}")
                        st.write(f"**Fecha:** {mov['fecha_movimiento']}")
                    
                    if mov.get('observaciones'):
                        st.write(f"**Observaciones:** {mov['observaciones']}")
        
        else:
            st.warning("No se encontraron movimientos en el período seleccionado")
    
    except Exception as e:
        st.error(f"Error cargando historial de movimientos: {str(e)}")
