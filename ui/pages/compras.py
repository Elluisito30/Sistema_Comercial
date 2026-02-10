"""
============================================
COMPRAS - GESTIÓN DE COMPRAS
============================================
Registrar y recibir compras a proveedores
"""

import streamlit as st
from services import CompraService, ProductoService
from repositories import ProveedorRepository
from exceptions import *
from datetime import datetime, date
import pandas as pd

def render():
    """Renderiza la página de compras"""
    
    st.markdown("<h1 class='main-header'>📥 Gestión de Compras</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Pestañas
    tab1, tab2, tab3 = st.tabs(["📝 Nueva Compra", "📦 Recibir Compra", "📋 Historial"])
    
    with tab1:
        nueva_compra()
    
    with tab2:
        recibir_compra()
    
    with tab3:
        historial_compras()


def nueva_compra():
    """Formulario para registrar una nueva compra"""
    
    st.subheader("📝 Nueva Orden de Compra")
    
    try:
        # Inicializar carrito de compras
        if 'carrito_compra' not in st.session_state:
            st.session_state.carrito_compra = []
        
        # ============================================
        # SECCIÓN 1: INFORMACIÓN DEL PROVEEDOR
        # ============================================
        
        st.markdown("### 🏭 Información del Proveedor")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            proveedor_repo = ProveedorRepository()
            proveedores = proveedor_repo.get_all_active()
            
            if not proveedores:
                st.error("⚠️ No hay proveedores registrados.")
                return
            
            proveedor_seleccionado = st.selectbox(
                "Proveedor",
                options=proveedores,
                format_func=lambda x: f"{x['ruc']} - {x['razon_social']}",
                key="proveedor_compra"
            )
        
        with col2:
            fecha_compra = st.date_input(
                "Fecha de Compra",
                value=date.today(),
                key="fecha_compra"
            )
        
        st.markdown("---")
        
        # ============================================
        # SECCIÓN 2: AGREGAR PRODUCTOS
        # ============================================
        
        st.markdown("### 📦 Productos a Comprar")
        
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            producto_service = ProductoService()
            productos = producto_service.listar_productos_activos()
            
            if not productos:
                st.error("⚠️ No hay productos disponibles")
                return
            
            producto_seleccionado = st.selectbox(
                "Producto",
                options=productos,
                format_func=lambda x: f"{x['codigo']} - {x['nombre']}",
                key="producto_compra"
            )
        
        with col2:
            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                value=1,
                step=1,
                key="cantidad_compra"
            )
        
        with col3:
            precio_unitario = st.number_input(
                "Precio Unit.",
                min_value=0.01,
                value=float(producto_seleccionado['precio_compra']),
                step=0.01,
                format="%.2f",
                key="precio_compra"
            )
        
        with col4:
            st.write("")
            st.write("")
            if st.button("➕ Agregar", use_container_width=True):
                agregar_al_carrito_compra(producto_seleccionado, cantidad, precio_unitario)
        
        # ============================================
        # SECCIÓN 3: MOSTRAR CARRITO DE COMPRA
        # ============================================
        
        if st.session_state.carrito_compra:
            st.markdown("#### 📦 Productos en la Orden")
            
            # Mostrar productos
            for idx, item in enumerate(st.session_state.carrito_compra):
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 0.5])
                
                with col1:
                    st.write(f"**{item['nombre']}**")
                with col2:
                    st.write(f"Cant: {item['cantidad']}")
                with col3:
                    st.write(f"S/. {item['precio_unitario']:.2f}")
                with col4:
                    st.write(f"**S/. {item['subtotal']:.2f}**")
                with col5:
                    if st.button("🗑️", key=f"eliminar_compra_{idx}"):
                        st.session_state.carrito_compra.pop(idx)
                        st.rerun()
            
            st.markdown("---")
            
            # ============================================
            # SECCIÓN 4: TOTALES Y CONFIRMACIÓN
            # ============================================
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                observaciones = st.text_area(
                    "Observaciones (opcional)",
                    placeholder="Ingrese observaciones adicionales...",
                    key="observaciones_compra"
                )
            
            with col2:
                # Calcular totales
                subtotal = sum(item['subtotal'] for item in st.session_state.carrito_compra)
                impuesto = subtotal * 0.18
                total = subtotal + impuesto
                
                st.metric("Subtotal", f"S/. {subtotal:.2f}")
                st.metric("IGV (18%)", f"S/. {impuesto:.2f}")
                st.metric("**TOTAL**", f"**S/. {total:.2f}**")
            
            st.markdown("---")
            
            # Botones de acción
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("✅ Registrar Compra", type="primary", use_container_width=True):
                    confirmar_compra(proveedor_seleccionado, fecha_compra, observaciones)
            
            with col2:
                if st.button("🗑️ Vaciar Carrito", use_container_width=True):
                    st.session_state.carrito_compra = []
                    st.rerun()
            
            with col3:
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state.carrito_compra = []
                    st.rerun()
        
        else:
            st.info("🛒 El carrito está vacío. Agregue productos para continuar.")
    
    except Exception as e:
        st.error(f"Error en el formulario de compra: {str(e)}")


def agregar_al_carrito_compra(producto, cantidad, precio_unitario):
    """Agrega un producto al carrito de compra"""
    
    try:
        # Verificar si el producto ya está en el carrito
        for item in st.session_state.carrito_compra:
            if item['producto_id'] == producto['id']:
                item['cantidad'] += cantidad
                item['subtotal'] = item['cantidad'] * item['precio_unitario']
                st.success(f"✅ Cantidad actualizada para {producto['nombre']}")
                st.rerun()
                return
        
        # Agregar nuevo item
        item = {
            'producto_id': producto['id'],
            'codigo': producto['codigo'],
            'nombre': producto['nombre'],
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
            'subtotal': cantidad * precio_unitario
        }
        
        st.session_state.carrito_compra.append(item)
        st.success(f"✅ {producto['nombre']} agregado a la orden")
        st.rerun()
    
    except Exception as e:
        st.error(f"Error agregando al carrito: {str(e)}")


def confirmar_compra(proveedor, fecha_compra, observaciones):
    """Confirma y registra la compra"""
    
    try:
        compra_service = CompraService()
        
        # Preparar lista de productos
        productos = [
            {
                'producto_id': item['producto_id'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio_unitario']
            }
            for item in st.session_state.carrito_compra
        ]
        
        # Registrar compra
        compra = compra_service.registrar_compra(
            proveedor_id=proveedor['id'],
            usuario_id=st.session_state.usuario_id,
            productos=productos,
            fecha_compra=fecha_compra,
            observaciones=observaciones
        )
        
        # Limpiar carrito
        st.session_state.carrito_compra = []
        
        # Mostrar confirmación
        st.success(f"✅ Compra registrada exitosamente!")
        st.balloons()
        
        st.info(f"""
        **Número de Compra:** {compra['numero_compra']}  
        **Proveedor:** {proveedor['razon_social']}  
        **Total:** S/. {compra['total']:.2f}  
        **Estado:** {compra['estado']}  
        **Productos:** {compra['cantidad_productos']}
        """)
        
        st.warning("⚠️ Recuerde recibir la mercancía en la pestaña 'Recibir Compra' para actualizar el inventario.")
    
    except Exception as e:
        st.error(f"Error registrando la compra: {str(e)}")


def recibir_compra():
    """Formulario para recibir una compra pendiente"""
    
    st.subheader("📦 Recibir Mercancía")
    
    try:
        compra_service = CompraService()
        
        # Obtener compras pendientes
        compras_pendientes = compra_service.listar_compras(estado='pendiente')
        
        if not compras_pendientes:
            st.info("📋 No hay compras pendientes por recibir")
            return
        
        st.info(f"📊 Compras pendientes: **{len(compras_pendientes)}**")
        
        # Seleccionar compra
        compra_seleccionada = st.selectbox(
            "Seleccionar Compra",
            options=compras_pendientes,
            format_func=lambda x: f"{x['numero_compra']} - {x['fecha_compra']} - {x.get('proveedor_nombre', 'N/A')} - S/. {x['total']:.2f}",
            key="compra_recibir"
        )
        
        if compra_seleccionada:
            st.markdown("---")
            
            # Mostrar detalles de la compra
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Número:** {compra_seleccionada['numero_compra']}")
                st.write(f"**Proveedor:** {compra_seleccionada.get('proveedor_nombre', 'N/A')}")
                st.write(f"**Fecha Compra:** {compra_seleccionada['fecha_compra']}")
            
            with col2:
                st.write(f"**Subtotal:** S/. {compra_seleccionada['subtotal']:.2f}")
                st.write(f"**IGV:** S/. {compra_seleccionada['impuesto']:.2f}")
                st.write(f"**TOTAL:** S/. {compra_seleccionada['total']:.2f}")
            
            if compra_seleccionada.get('observaciones'):
                st.write(f"**Observaciones:** {compra_seleccionada['observaciones']}")
            
            st.markdown("---")
            
            # Obtener detalles de los productos
            detalles = compra_service.obtener_detalles_compra(compra_seleccionada['id'])
            
            if detalles:
                st.markdown("#### 📦 Productos en la Compra")
                
                for detalle in detalles:
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{detalle.get('producto_nombre', 'N/A')}**")
                    with col2:
                        st.write(f"Cantidad: {detalle['cantidad']}")
                    with col3:
                        st.write(f"P.U.: S/. {detalle['precio_unitario']:.2f}")
                    with col4:
                        st.write(f"Subtotal: S/. {detalle['subtotal']:.2f}")
            
            st.markdown("---")
            
            # Fecha de recepción
            fecha_recepcion = st.date_input(
                "Fecha de Recepción",
                value=date.today(),
                key="fecha_recepcion"
            )
            
            observaciones_recepcion = st.text_area(
                "Observaciones de Recepción (opcional)",
                placeholder="Ingrese observaciones sobre la recepción...",
                key="obs_recepcion"
            )
            
            # Botones de acción
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Confirmar Recepción", type="primary", use_container_width=True):
                    try:
                        compra_service.recibir_compra(
                            compra_id=compra_seleccionada['id'],
                            fecha_recepcion=fecha_recepcion,
                            usuario_id=st.session_state.usuario_id,
                            observaciones=observaciones_recepcion
                        )
                        
                        st.success("✅ Compra recibida exitosamente!")
                        st.success("📦 Inventario actualizado correctamente")
                        st.balloons()
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error recibiendo la compra: {str(e)}")
            
            with col2:
                if st.button("❌ Cancelar Compra", use_container_width=True):
                    if st.checkbox("Confirmar cancelación", key="confirmar_cancelar"):
                        try:
                            compra_service.cancelar_compra(compra_seleccionada['id'])
                            st.success("✅ Compra cancelada")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error cancelando la compra: {str(e)}")
    
    except Exception as e:
        st.error(f"Error en recepción de compras: {str(e)}")


def historial_compras():
    """Muestra el historial de compras"""
    
    st.subheader("📋 Historial de Compras")
    
    try:
        compra_service = CompraService()
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            estado = st.selectbox(
                "Estado",
                options=["Todas", "pendiente", "recibida", "cancelada"],
                key="filtro_estado_compra"
            )
        
        with col2:
            fecha_inicio = st.date_input(
                "Fecha Inicio",
                value=date.today().replace(day=1),
                key="fecha_inicio_compra"
            )
        
        with col3:
            fecha_fin = st.date_input(
                "Fecha Fin",
                value=date.today(),
                key="fecha_fin_compra"
            )
        
        # Obtener compras
        if estado == "Todas":
            compras = compra_service.listar_compras(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        else:
            compras = compra_service.listar_compras(estado=estado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        
        if compras:
            st.info(f"📊 Total de compras: **{len(compras)}** | Monto total: **S/. {sum(c['total'] for c in compras):,.2f}**")
            
            # Mostrar compras
            for compra in compras:
                estado_emoji = {
                    'pendiente': '⏳',
                    'recibida': '✅',
                    'cancelada': '❌'
                }
                
                with st.expander(
                    f"{estado_emoji.get(compra['estado'], '📄')} {compra['numero_compra']} - {compra['fecha_compra']} - S/. {compra['total']:.2f} - {compra['estado'].upper()}"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Proveedor:** {compra.get('proveedor_nombre', 'N/A')}")
                        st.write(f"**Fecha Compra:** {compra['fecha_compra']}")
                        if compra.get('fecha_recepcion'):
                            st.write(f"**Fecha Recepción:** {compra['fecha_recepcion']}")
                    
                    with col2:
                        st.write(f"**Subtotal:** S/. {compra['subtotal']:.2f}")
                        st.write(f"**IGV:** S/. {compra['impuesto']:.2f}")
                        st.write(f"**TOTAL:** S/. {compra['total']:.2f}")
                    
                    if compra.get('observaciones'):
                        st.write(f"**Observaciones:** {compra['observaciones']}")
        
        else:
            st.warning("No se encontraron compras en el período seleccionado")
    
    except Exception as e:
        st.error(f"Error cargando historial de compras: {str(e)}")
