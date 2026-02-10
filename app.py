"""
============================================
SISTEMA DE COMERCIALIZACIÓN
Aplicación Principal Streamlit
============================================
"""

import streamlit as st
from pathlib import Path
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.database import initialize_pool, test_connection
from config.settings import AppConfig

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================

st.set_page_config(
    page_title="Sistema de Comercialización",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# ESTILOS CSS PERSONALIZADOS
# ============================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .warning-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# INICIALIZACIÓN
# ============================================

@st.cache_resource
def init_database():
    """Inicializa la conexión a la base de datos"""
    try:
        initialize_pool()
        test_connection()
        return True
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return False

# Inicializar base de datos
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = init_database()

if not st.session_state.db_initialized:
    st.error("⚠️ No se pudo conectar a la base de datos. Verifica la configuración.")
    st.stop()

# ============================================
# INICIALIZAR SESSION STATE
# ============================================

if 'usuario_id' not in st.session_state:
    st.session_state.usuario_id = 1  # Usuario por defecto (admin)

if 'usuario_nombre' not in st.session_state:
    st.session_state.usuario_nombre = "Administrador"

if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# ============================================
# MENÚ DE NAVEGACIÓN
# ============================================

st.sidebar.markdown("### 🛒 Sistema de Comercialización")
st.sidebar.markdown("---")

# Información del usuario
st.sidebar.info(f"👤 Usuario: {st.session_state.usuario_nombre}")
st.sidebar.markdown("---")

# Menú de navegación
menu_options = {
    "🏠 Dashboard": "dashboard",
    "📦 Productos": "productos",
    "🛍️ Ventas": "ventas",
    "📥 Compras": "compras",
    "📊 Inventario": "inventario"
}

selected_page = st.sidebar.radio(
    "Navegación",
    list(menu_options.keys()),
    key="navigation"
)

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Sistema de Comercialización v1.0")

# ============================================
# ENRUTAMIENTO DE PÁGINAS
# ============================================

page = menu_options[selected_page]

if page == "dashboard":
    from ui.pages import dashboard
    dashboard.render()

elif page == "productos":
    from ui.pages import productos
    productos.render()

elif page == "ventas":
    from ui.pages import ventas
    ventas.render()

elif page == "compras":
    from ui.pages import compras
    compras.render()

elif page == "inventario":
    from ui.pages import inventario
    inventario.render()
