"""
============================================
VENTAS - REGISTRO DE VENTAS
============================================
Registrar ventas con validación de stock
"""

import streamlit as st
from services import VentaService, ProductoService
from repositories import ClienteRepository
from exceptions import *
from datetime import datetime, date
import pandas as pd

def render():
    """Renderiza la página de ventas"""
    
    st.markdown("<h1 class='main-header'>🛍️ Registro de Ventas</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Pestañas
    tab1, tab2 = st.tabs(["🛒 Nueva Venta", "📋 Historial de Ventas"])
    
    with tab1:
        nueva_venta()
    
    with tab2:
        historial_ventas()


def nueva_venta():
    """Formulario para registrar una nueva venta"""
    
    st.subheader("🛒 Nueva Venta")
    
    try:
        # Inicializar carrito en session_state si no existe
        if 'carrito_venta' not in st.session_state:
            st.session_state.carrito_venta = []
        
        # ============================================
        # SECCIÓN 1: INFORMACIÓN DEL CLIENTE
        # ============================================
        
        st.markdown("### 👤 Información del Cliente")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            cliente_repo = ClienteRepository()
            clientes = cliente_repo.get_all_active()
            
            if not clientes:
                st.error("⚠️ No hay clientes registrados. Por favor, registre un cliente primero.")
                return
            
            cliente_seleccionado = st.selectbox(
                "Cliente",
                options=clientes,
                format_func=lambda x: f"{x['numero_documento']} - {x['nombres']} {x.get('apellidos', '')}",
                key="cliente_venta"
            )
        
        with col2:
            tipo_comprobante = st.selectbox(
                "Tipo de Comprobante",
                options=["boleta", "factura", "ticket"],
                key="tipo_comprobante"
            )
        
        st.markdown("---")
        
        # ============================================
        # SECCIÓN 2: AGREGAR PRODUCTOS AL CARRITO
        # ============================================
        
        st.markdown("### 🛒 Carrito de Compra")
        
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
                format_func=lambda x: f"{x['codigo']} - {x['nombre']} (Stock: {x['stock_actual']})",
                key="producto_venta"
            )
        
        with col2:
            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                value=1,
                step=1,
                key="cantidad_venta"
            )
        
        with col3:
            precio_unitario = st.number_input(
                "Precio Unit.",
                min_value=0.01,
                value=float(producto_seleccionado['precio_venta']),
                step=0.01,
                format="%.2f",
                key="precio_venta"
            )
        
        with col4:
            st.write("")  # Espaciado
            st.write("")
            if st.button("➕ Agregar", use_container_width=True):
                agregar_al_carrito(producto_seleccionado, cantidad, precio_unitario)
        
        # ============================================
        # SECCIÓN 3: MOSTRAR CARRITO
        # ============================================
        
        if st.session_state.carrito_venta:
            st.markdown("#### 📦 Productos en el Carrito")
            
            # Mostrar productos en el carrito
            for idx, item in enumerate(st.session_state.carrito_venta):
                col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 0.5])
                
                with col1:
                    st.write(f"**{item['nombre']}**")
                with col2:
                    st.write(f"Stock: {item['stock_disponible']}")
                with col3:
                    st.write(f"Cant: {item['cantidad']}")
                with col4:
                    st.write(f"S/. {item['precio_unitario']:.2f}")
                with col5:
                    st.write(f"**S/. {item['subtotal']:.2f}**")
                with col6:
                    if st.button("🗑️", key=f"eliminar_{idx}"):
                        st.session_state.carrito_venta.pop(idx)
                        st.rerun()
            
            st.markdown("---")
            
            # ============================================
            # SECCIÓN 4: TOTALES Y CONFIRMACIÓN
            # ============================================
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                metodo_pago = st.selectbox(
                    "Método de Pago",
                    options=["efectivo", "tarjeta", "transferencia"],
                    key="metodo_pago"
                )
                
                observaciones = st.text_area(
                    "Observaciones (opcional)",
                    placeholder="Ingrese observaciones adicionales...",
                    key="observaciones_venta"
                )
            
            with col2:
                # Calcular totales
                subtotal = sum(item['subtotal'] for item in st.session_state.carrito_venta)
                descuento_global = st.number_input(
                    "Descuento Global (S/.)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    key="descuento_venta"
                )
                impuesto = (subtotal - descuento_global) * 0.18
                total = subtotal - descuento_global + impuesto
                
                st.metric("Subtotal", f"S/. {subtotal:.2f}")
                st.metric("Descuento", f"S/. {descuento_global:.2f}")
                st.metric("IGV (18%)", f"S/. {impuesto:.2f}")
                st.metric("**TOTAL**", f"**S/. {total:.2f}**")
            
            st.markdown("---")
            
            # Botones de acción
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("✅ Confirmar Venta", type="primary", use_container_width=True):
                    confirmar_venta(
                        cliente_seleccionado,
                        tipo_comprobante,
                        metodo_pago,
                        descuento_global,
                        observaciones
                    )
            
            with col2:
                if st.button("🗑️ Vaciar Carrito", use_container_width=True):
                    st.session_state.carrito_venta = []
                    st.rerun()
            
            with col3:
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state.carrito_venta = []
                    st.rerun()
        
        else:
            st.info("🛒 El carrito está vacío. Agregue productos para continuar.")
    
    except Exception as e:
        st.error(f"Error en el formulario de venta: {str(e)}")


def agregar_al_carrito(producto, cantidad, precio_unitario):
    """Agrega un producto al carrito"""
    
    try:
        # Validar stock disponible
        if producto['stock_actual'] < cantidad:
            st.error(f"⚠️ Stock insuficiente. Disponible: {producto['stock_actual']}")
            return
        
        # Verificar si el producto ya está en el carrito
        for item in st.session_state.carrito_venta:
            if item['producto_id'] == producto['id']:
                # Actualizar cantidad si ya existe
                nueva_cantidad = item['cantidad'] + cantidad
                if nueva_cantidad > producto['stock_actual']:
                    st.error(f"⚠️ Stock insuficiente. Disponible: {producto['stock_actual']}")
                    return
                item['cantidad'] = nueva_cantidad
                item['subtotal'] = item['cantidad'] * item['precio_unitario']
                st.success(f"✅ Cantidad actualizada para {producto['nombre']}")
                st.rerun()
                return
        
        # Agregar nuevo item al carrito
        item = {
            'producto_id': producto['id'],
            'codigo': producto['codigo'],
            'nombre': producto['nombre'],
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
            'subtotal': cantidad * precio_unitario,
            'descuento': 0,
            'stock_disponible': producto['stock_actual']
        }
        
        st.session_state.carrito_venta.append(item)
        st.success(f"✅ {producto['nombre']} agregado al carrito")
        st.rerun()
    
    except Exception as e:
        st.error(f"Error agregando al carrito: {str(e)}")


def confirmar_venta(cliente, tipo_comprobante, metodo_pago, descuento_global, observaciones):
    """Confirma y registra la venta"""
    
    try:
        venta_service = VentaService()
        
        # Preparar lista de productos
        productos = [
            {
                'producto_id': item['producto_id'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio_unitario'],
                'descuento': item.get('descuento', 0)
            }
            for item in st.session_state.carrito_venta
        ]
        
        # Registrar venta
        venta = venta_service.registrar_venta(
            cliente_id=cliente['id'],
            usuario_id=st.session_state.usuario_id,
            productos=productos,
            tipo_comprobante=tipo_comprobante,
            metodo_pago=metodo_pago,
            fecha_venta=date.today(),
            descuento_global=descuento_global,
            observaciones=observaciones
        )
        
        # Limpiar carrito
        st.session_state.carrito_venta = []
        
        # Mostrar confirmación
        st.success(f"✅ Venta registrada exitosamente!")
        st.balloons()
        
        # Mostrar detalles de la venta
        st.info(f"""
        **Número de Venta:** {venta['numero_venta']}  
        **Cliente:** {cliente['nombres']} {cliente.get('apellidos', '')}  
        **Total:** S/. {venta['total']:.2f}  
        **Productos:** {venta['cantidad_productos']}
        """)
        
        # Botón para ver detalles
        if st.button("Ver Detalles"):
            st.json(venta)
    
    except StockInsuficienteException as e:
        st.error(f"⚠️ {e.message}")
        st.error(f"Producto: {e.details['producto']}")
        st.error(f"Stock disponible: {e.details['stock_disponible']}")
        st.error(f"Cantidad solicitada: {e.details['cantidad_solicitada']}")
    
    except Exception as e:
        st.error(f"Error registrando la venta: {str(e)}")


def historial_ventas():
    """Muestra el historial de ventas"""
    
    st.subheader("📋 Historial de Ventas")
    
    try:
        venta_service = VentaService()
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            estado = st.selectbox(
                "Estado",
                options=["Todas", "completada", "anulada"],
                key="filtro_estado_venta"
            )
        
        with col2:
            fecha_inicio = st.date_input(
                "Fecha Inicio",
                value=date.today().replace(day=1),
                key="fecha_inicio_venta"
            )
        
        with col3:
            fecha_fin = st.date_input(
                "Fecha Fin",
                value=date.today(),
                key="fecha_fin_venta"
            )
        
        # Obtener ventas
        if estado == "Todas":
            ventas = venta_service.listar_ventas(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        else:
            ventas = venta_service.listar_ventas(estado=estado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        
        if ventas:
            st.info(f"📊 Total de ventas: **{len(ventas)}** | Monto total: **S/. {sum(v['total'] for v in ventas):,.2f}**")
            
            # Mostrar ventas
            for venta in ventas:
                with st.expander(
                    f"🧾 {venta['numero_venta']} - {venta['fecha_venta']} - S/. {venta['total']:.2f} - {venta['estado'].upper()}"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Cliente:** {venta.get('cliente_nombre', 'N/A')}")
                        st.write(f"**Comprobante:** {venta['tipo_comprobante']}")
                        st.write(f"**Método de Pago:** {venta['metodo_pago']}")
                    
                    with col2:
                        st.write(f"**Subtotal:** S/. {venta['subtotal']:.2f}")
                        st.write(f"**Descuento:** S/. {venta['descuento']:.2f}")
                        st.write(f"**IGV:** S/. {venta['impuesto']:.2f}")
                        st.write(f"**TOTAL:** S/. {venta['total']:.2f}")
                    
                    if venta.get('observaciones'):
                        st.write(f"**Observaciones:** {venta['observaciones']}")
                    
                    # Botón para anular (si está completada)
                    if venta['estado'] == 'completada':
                        if st.button(f"❌ Anular Venta", key=f"anular_{venta['id']}"):
                            try:
                                venta_service.anular_venta(venta['id'], st.session_state.usuario_id)
                                st.success("✅ Venta anulada exitosamente")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error anulando venta: {str(e)}")
        
        else:
            st.warning("No se encontraron ventas en el período seleccionado")
    
    except Exception as e:
        st.error(f"Error cargando historial de ventas: {str(e)}")
