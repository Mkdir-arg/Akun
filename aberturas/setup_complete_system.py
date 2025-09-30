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
    
    # 2. Crear roles
    roles_code = """
from apps.accounts.models import Role
roles = [
    ('Administrador', 'Acceso completo al sistema'),
    ('Vendedor', 'Gestión de ventas y clientes'),
    ('Operador', 'Operaciones básicas'),
    ('Consulta', 'Solo lectura'),
    ('Colocadores', 'Gestión de instalaciones')
]
for name, description in roles:
    Role.objects.get_or_create(name=name, defaults={'description': description})
print(f'✅ Roles creados: {Role.objects.count()}')
"""
    run_command("Creando roles", roles_code)
    
    # 3. Crear superusuario
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
    
    # 4. Cargar datos básicos del catálogo
    run_command("Cargando datos básicos del catálogo", ["python", "/app/create_basic_data.py"])
    
    # 5. Cargar impuestos
    impuestos_code = """
from apps.catalog.models import TasaImpuesto
impuestos = [
    ('IVA 21%', 21.00, True),
    ('IVA 10.5%', 10.50, False),
    ('IVA 27%', 27.00, False),
    ('Exento', 0.00, False)
]
for name, rate, is_default in impuestos:
    TasaImpuesto.objects.get_or_create(name=name, defaults={'rate': rate, 'is_default': is_default})
print(f'✅ Impuestos creados: {TasaImpuesto.objects.count()}')
"""
    run_command("Creando impuestos", impuestos_code)
    
    # 6. Cargar monedas
    monedas_code = """
from apps.core.models import Moneda
monedas = [
    ('ARS', 'Peso Argentino', '$', True),
    ('USD', 'Dólar Estadounidense', 'US$', False),
    ('EUR', 'Euro', '€', False)
]
for code, name, symbol, is_default in monedas:
    Moneda.objects.get_or_create(code=code, defaults={'name': name, 'symbol': symbol, 'is_default': is_default})
print(f'✅ Monedas creadas: {Moneda.objects.count()}')
"""
    run_command("Creando monedas", monedas_code)
    
    # 7. Cargar parametría del sistema
    run_command("Cargando parametría del sistema", ["python", "/app/load_system_data.py"])
    
    # 8. Cargar unidades de medida
    run_command("Cargando unidades de medida", ["python", "/app/create_units.py"])
    
    # 9. Cargar datos geográficos
    run_command("Cargando datos geográficos", ["python", "manage.py", "loaddata", "fixtures/localidad_municipio_provincia.json"])
    

    print("📊 Resumen:")
    
    # Mostrar resumen de datos cargados
    summary_code = """
from apps.accounts.models import Role
from apps.core.models import Moneda, Provincia, Municipio, Localidad
from apps.catalog.models import CategoriaProducto, TasaImpuesto, UnidadMedida, ListaPrecios, ColorProducto, LineaProducto
from apps.crm.models import TerminoPago, EtiquetaCliente
from django.contrib.auth import get_user_model
User = get_user_model()

print(f'   - Usuarios: {User.objects.count()}')
print(f'   - Roles: {Role.objects.count()}')
print(f'   - Monedas: {Moneda.objects.count()}')
print(f'   - Categorías: {CategoriaProducto.objects.count()}')
print(f'   - Tasas de impuesto: {TasaImpuesto.objects.count()}')
print(f'   - Unidades de medida: {UnidadMedida.objects.count()}')
print(f'   - Listas de precios: {ListaPrecios.objects.count()}')
print(f'   - Términos de pago: {TerminoPago.objects.count()}')
print(f'   - Etiquetas de cliente: {EtiquetaCliente.objects.count()}')
print(f'   - Colores: {ColorProducto.objects.count()}')
print(f'   - Líneas: {LineaProducto.objects.count()}')
print(f'   - Provincias: {Provincia.objects.count()}')
print(f'   - Municipios: {Municipio.objects.count()}')
print(f'   - Localidades: {Localidad.objects.count()}')
"""
    run_command("Generando resumen", summary_code)

if __name__ == "__main__":
    main()