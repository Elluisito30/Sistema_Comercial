"""
============================================
DASHBOARD - PÁGINA PRINCIPAL
============================================
Vista general del sistema con métricas clave
"""

import streamlit as st
from services import ProductoService, InventarioService
from datetime import datetime

def render():
    """Renderiza la página del dashboard"""
    
    st.markdown("<h1 class='main-header'>📊 Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    try:
        # Inicializar servicios
        producto_service = ProductoService()
        inventario_service = InventarioService()
        
        # ============================================
        # MÉTRICAS PRINCIPALES
        # ============================================
        
        st.subheader("📈 Métricas Generales")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            productos = producto_service.listar_productos_activos()
            st.metric(
                label="Total Productos",
                value=len(productos),
                delta="Activos"
            )
        
        with col2:
            stock_critico = producto_service.obtener_productos_stock_critico()
            st.metric(
                label="Stock Crítico",
                value=len(stock_critico),
                delta="Alerta",
                delta_color="inverse"
            )
        
        with col3:
            valor_inventario = inventario_service.calcular_valor_total_inventario()
            st.metric(
                label="Valor Inventario",
                value=f"S/. {valor_inventario['valor_venta']:,.2f}",
                delta=f"{valor_inventario['margen_porcentaje']:.1f}% margen"
            )
        
        with col4:
            st.metric(
                label="Total Unidades",
                value=f"{valor_inventario['total_unidades']:,}",
                delta=f"{valor_inventario['total_productos']} productos"
            )
        
        st.markdown("---")
        
        # ============================================
        # ALERTAS DE STOCK CRÍTICO
        # ============================================
        
        if stock_critico and len(stock_critico) > 0:
            st.warning(f"⚠️ **{len(stock_critico)} productos** con stock crítico")
            
            with st.expander("Ver productos con stock bajo", expanded=False):
                for producto in stock_critico[:5]:  # Mostrar solo los primeros 5
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{producto['nombre']}**")
                    with col2:
                        st.write(f"Stock: {producto['stock_actual']}")
                    with col3:
                        st.write(f"Mínimo: {producto['stock_minimo']}")
                        
                if len(stock_critico) > 5:
                    st.info(f"Y {len(stock_critico) - 5} productos más...")
        else:
            st.success("✅ Todos los productos tienen stock suficiente")
        
        st.markdown("---")
        
        # ============================================
        # INFORMACIÓN DEL SISTEMA
        # ============================================
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Valorización del Inventario")
            st.write(f"**Valor de Compra:** S/. {valor_inventario['valor_compra']:,.2f}")
            st.write(f"**Valor de Venta:** S/. {valor_inventario['valor_venta']:,.2f}")
            st.write(f"**Ganancia Potencial:** S/. {valor_inventario['ganancia_potencial']:,.2f}")
            st.write(f"**Margen:** {valor_inventario['margen_porcentaje']:.2f}%")
        
        with col2:
            st.subheader("📅 Información del Sistema")
            st.write(f"**Fecha:** {datetime.now().strftime('%d/%m/%Y')}")
            st.write(f"**Hora:** {datetime.now().strftime('%H:%M:%S')}")
            st.write(f"**Usuario:** {st.session_state.usuario_nombre}")
    
    except Exception as e:
        st.error(f"Error cargando el dashboard: {str(e)}")
        if st.button("🔄 Reintentar"):
            st.rerun()
