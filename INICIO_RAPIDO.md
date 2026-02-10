# ============================================
# GUÍA DE INICIO RÁPIDO
# Sistema de Comercialización
# ============================================

## 🚀 Pasos para Ejecutar la Aplicación

### 1. Verificar Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Base de Datos

Asegúrate de que tu archivo `.env` esté configurado correctamente:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=sistema_comercializacion
```

### 3. Verificar Conexión a la Base de Datos

```bash
python test_connection.py
```

Deberías ver:
```
✓ Conexión exitosa
✓ Pool funcionando correctamente
✓ Consulta ejecutada correctamente
```

### 4. Iniciar la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

---

## 📱 Uso de la Aplicación

### Navegación

El sistema tiene un menú lateral con las siguientes opciones:

1. **🏠 Dashboard**: Vista general con métricas principales
2. **📦 Productos**: Gestión completa del catálogo
3. **🛍️ Ventas**: Registro y consulta de ventas
4. **📥 Compras**: Órdenes de compra y recepción
5. **📊 Inventario**: Consulta, ajustes y movimientos

### Flujo de Trabajo Típico

#### A. Registrar Productos
1. Ir a **📦 Productos**
2. Pestaña "➕ Crear Producto"
3. Llenar formulario y guardar

#### B. Registrar una Compra
1. Ir a **📥 Compras**
2. Pestaña "📝 Nueva Compra"
3. Seleccionar proveedor
4. Agregar productos al carrito
5. Confirmar compra (estado: PENDIENTE)

#### C. Recibir Mercancía
1. Ir a **📥 Compras**
2. Pestaña "📦 Recibir Compra"
3. Seleccionar compra pendiente
4. Confirmar recepción
5. El stock se actualiza automáticamente

#### D. Realizar una Venta
1. Ir a **🛍️ Ventas**
2. Pestaña "🛒 Nueva Venta"
3. Seleccionar cliente
4. Agregar productos al carrito (valida stock automáticamente)
5. Confirmar venta
6. El stock se descuenta automáticamente

#### E. Consultar Inventario
1. Ir a **📊 Inventario**
2. Ver stock general, productos críticos o historial

---

## 🔧 Solución de Problemas Comunes

### Error: "No se pudo conectar a la base de datos"
- ✅ Verificar que MySQL esté corriendo
- ✅ Revisar credenciales en el archivo `.env`
- ✅ Verificar que la base de datos `sistema_comercializacion` exista

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt --force-reinstall
```

### Puerto 8501 ocupado
```bash
streamlit run app.py --server.port 8502
```

### Ver logs de errores
Los logs están en: `logs/database.log`

---

## 📊 Datos de Prueba

El sistema viene con datos de prueba incluidos:

- **Usuarios**: admin, vendedor1, almacen1 (password: admin123)
- **7 Categorías** de productos
- **3 Proveedores**
- **5 Clientes**
- **20 Productos** de diferentes categorías

---

## 💡 Tips de Uso

1. **Stock Crítico**: El dashboard muestra alertas cuando los productos alcanzan el stock mínimo
2. **Búsqueda**: Puedes buscar productos por código o nombre en todas las pantallas
3. **Filtros**: Usa los filtros de categoría y fecha para encontrar información rápidamente
4. **Exportar**: Los listados de productos e inventario se pueden exportar a CSV
5. **Validaciones**: El sistema valida automáticamente stock antes de vender

---

## 🎯 Atajos de Teclado

- **Ctrl + R**: Recargar la página
- **Ctrl + +/-**: Zoom in/out
- **Tab**: Navegar entre campos de formulario

---

## 📞 Ayuda

Si encuentras algún problema o tienes dudas:

1. Revisa los logs en `logs/database.log`
2. Ejecuta `python test_connection.py` para diagnosticar problemas de conexión
3. Ejecuta `python test_repositories.py` para probar los repositorios
4. Ejecuta `python test_services.py` para probar los servicios

---

**¡Listo para usar! 🚀**
