"""
Prueba simple de conexión a Neon
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("=" * 60)
print("🔍 PROBANDO CONEXIÓN A NEON")
print("=" * 60)

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL no está configurado en .env")
    exit(1)

print(f"\n📡 Conectando a Neon...")

try:
    # Conectar
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # 1. Verificar versión
    print("\n1️⃣ Verificando versión de PostgreSQL...")
    cur.execute("SELECT version()")
    version = cur.fetchone()[0]
    print(f"   ✅ {version[:80]}...")
    
    # 2. Verificar base de datos
    cur.execute("SELECT current_database()")
    db_name = cur.fetchone()[0]
    print(f"\n2️⃣ Base de datos: {db_name}")
    
    # 3. Listar tablas
    print("\n3️⃣ Tablas disponibles:")
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tablas = cur.fetchall()
    for tabla in tablas:
        print(f"   - {tabla[0]}")
    
    # 4. Datos de ejemplo
    print("\n4️⃣ Datos de ejemplo (categorías):")
    cur.execute("SELECT COUNT(*) FROM categorias")
    count = cur.fetchone()[0]
    print(f"   Total de categorías: {count}")
    
    cur.execute("SELECT nombre, descripcion FROM categorias LIMIT 5")
    categorias = cur.fetchall()
    for cat in categorias:
        print(f"   - {cat[0]}: {cat[1]}")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("🎉 ¡TODO FUNCIONA CORRECTAMENTE!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()