"""
============================================
COMPONENTE CARRITO
============================================
Componente reutilizable para carrito de compras/ventas
"""

import streamlit as st


def mostrar_carrito(items, tipo="venta"):
    """
    Muestra el carrito de compras o ventas
    
    Args:
        items (list): Lista de items en el carrito
        tipo (str): 'venta' o 'compra'
    """
    
    if not items:
        st.info("🛒 El carrito está vacío")
        return
    
    st.markdown("#### 🛒 Carrito")
    
    total = 0
    
    for idx, item in enumerate(items):
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 0.5])
        
        with col1:
            st.write(f"**{item['nombre']}**")
        
        with col2:
            st.write(f"Cant: {item['cantidad']}")
        
        with col3:
            st.write(f"P.U.: S/. {item['precio_unitario']:.2f}")
        
        with col4:
            subtotal = item['cantidad'] * item['precio_unitario']
            st.write(f"**S/. {subtotal:.2f}**")
            total += subtotal
        
        with col5:
            if st.button("🗑️", key=f"eliminar_{tipo}_{idx}"):
                return idx  # Retorna el índice a eliminar
    
    st.markdown("---")
    st.write(f"### Total: S/. {total:.2f}")
    
    return None


def calcular_totales(items, descuento_global=0, impuesto_porcentaje=0.18):
    """
    Calcula los totales del carrito
    
    Args:
        items (list): Lista de items
        descuento_global (float): Descuento global
        impuesto_porcentaje (float): Porcentaje de impuesto
        
    Returns:
        dict: Diccionario con los totales
    """
    
    subtotal = sum(item['cantidad'] * item['precio_unitario'] for item in items)
    subtotal_con_descuento = subtotal - descuento_global
    impuesto = subtotal_con_descuento * impuesto_porcentaje
    total = subtotal_con_descuento + impuesto
    
    return {
        'subtotal': round(subtotal, 2),
        'descuento': round(descuento_global, 2),
        'impuesto': round(impuesto, 2),
        'total': round(total, 2)
    }
