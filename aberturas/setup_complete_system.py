#!/usr/bin/env python
import os
import sys
import django
import subprocess

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aberturas.settings.dev')
django.setup()

def run_command(description, command):
    print(f"🔄 {description}...")
    try:
        if isinstance(command, list):
            subprocess.run(command, check=True)
        else:
            exec(command)
        print(f"✅ {description} completado")
        return True
    except Exception as e:
        print(f"❌ Error en {description}: {e}")
        return False

def main():
    print("🚀 Iniciando configuración completa del sistema...")
    
    # 1. Aplicar migraciones
    run_command("Aplicando migraciones", ["python", "manage.py", "migrate"])
    
    # 2. Crear superusuario
    superuser_code = """
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin@akun.com', 'admin@akun.com', 'admin123')
    print('👤 Superusuario creado: admin@akun.com / admin123')
else:
    print('👤 Superusuario ya existe')
"""
    run_command("Creando superusuario", superuser_code)
    
    # 3. Cargar datos básicos
    run_command("Cargando datos básicos", ["python", "/app/create_basic_data.py"])
    
    # 4. Cargar parametría del sistema
    run_command("Cargando parametría del sistema", ["python", "/app/load_system_data.py"])
    
    # 5. Cargar unidades de medida
    run_command("Cargando unidades de medida", ["python", "/app/create_units.py"])
    
    # 6. Cargar datos geográficos
    run_command("Cargando datos geográficos", ["python", "manage.py", "loaddata", "fixtures/localidad_municipio_provincia.json"])
    
    print("🎉 ¡Sistema completamente configurado!")
    print("📋 Credenciales: admin@akun.com / admin123")
    print("🌐 Admin: https://z5906h8z-8002.brs.devtunnels.ms/admin")

if __name__ == "__main__":
    main()