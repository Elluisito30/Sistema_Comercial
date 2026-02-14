"""Verifica que psycopg2 esté instalado"""
try:
    import psycopg2
    print("✅ psycopg2 está instalado correctamente")
    print(f"   Versión: {psycopg2.__version__}")
    
    # Probar conexión rápida
    from config.database import test_connection
    if test_connection():
        print("✅ Conexión a PostgreSQL exitosa")
except ImportError as e:
    print(f"❌ Error: {e}")
    print("   Solución: pip install psycopg2-binary")
except Exception as e:
    print(f"⚠️  Conexión fallida: {e}")