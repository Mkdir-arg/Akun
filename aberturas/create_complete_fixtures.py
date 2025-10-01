#!/usr/bin/env python
"""
Script para crear fixtures completos del sistema de aberturas
Incluye toda la información base: plantillas, productos, clientes, etc.
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aberturas.settings.dev')
django.setup()

from django.core.management import call_command

def create_fixtures():
    """Crear todos los fixtures del sistema"""
    
    print("🔧 CREANDO FIXTURES DEL SISTEMA DE ABERTURAS")
    print("=" * 50)
    
    # Crear directorio de fixtures
    fixtures_dir = 'fixtures'
    os.makedirs(fixtures_dir, exist_ok=True)
    
    # Timestamp para identificar la versión
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    fixtures_config = [
        {
            'name': 'Plantillas de Productos',
            'models': ['catalog.ProductTemplate'],
            'file': f'{fixtures_dir}/01_product_templates_{timestamp}.json',
            'description': '111 plantillas base del sistema'
        },
        {
            'name': 'Atributos de Plantillas', 
            'models': ['catalog.TemplateAttribute'],
            'file': f'{fixtures_dir}/02_template_attributes_{timestamp}.json',
            'description': 'Definición de línea, marco, hoja, interior'
        },
        {
            'name': 'Opciones de Atributos',
            'models': ['catalog.AttributeOption'], 
            'file': f'{fixtures_dir}/03_attribute_options_{timestamp}.json',
            'description': '229 marcos + 421 hojas + 480 interiores'
        },
        {
            'name': 'Productos Originales',
            'models': ['catalog.Product'],
            'file': f'{fixtures_dir}/04_products_{timestamp}.json', 
            'description': 'Productos del sistema original'
        },
        {
            'name': 'Listas de Precios',
            'models': ['catalog.PriceList', 'catalog.PriceListItem'],
            'file': f'{fixtures_dir}/05_pricelists_{timestamp}.json',
            'description': 'Precios y configuraciones'
        },
        {
            'name': 'Clientes CRM',
            'models': ['crm.Cliente'],
            'file': f'{fixtures_dir}/06_clientes_{timestamp}.json',
            'description': 'Base de clientes'
        },
        {
            'name': 'Presupuestos',
            'models': ['sales.Presupuesto', 'sales.LineaPresupuesto'],
            'file': f'{fixtures_dir}/07_presupuestos_{timestamp}.json',
            'description': 'Presupuestos con plantillas'
        },
        {
            'name': 'Usuarios y Grupos',
            'models': ['auth.User', 'auth.Group', 'auth.Permission'],
            'file': f'{fixtures_dir}/08_auth_{timestamp}.json',
            'description': 'Sistema de autenticación'
        }
    ]
    
    # Generar fixtures individuales
    for config in fixtures_config:
        try:
            print(f"\n📦 {config['name']}")
            print(f"   {config['description']}")
            
            call_command(
                'dumpdata',
                *config['models'],
                output=config['file'],
                format='json',
                indent=2,
                verbosity=0
            )
            
            # Verificar tamaño del archivo
            if os.path.exists(config['file']):
                size = os.path.getsize(config['file'])
                size_kb = size / 1024
                print(f"   ✓ Creado: {config['file']} ({size_kb:.1f} KB)")
            else:
                print(f"   ⚠ No se pudo crear: {config['file']}")
                
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
    
    # Crear fixture completo del sistema
    print(f"\n🎯 FIXTURE COMPLETO DEL SISTEMA")
    complete_file = f'{fixtures_dir}/sistema_completo_{timestamp}.json'
    
    try:
        call_command(
            'dumpdata',
            '--exclude=contenttypes',
            '--exclude=sessions.session',
            '--exclude=admin.logentry',
            '--exclude=auth.permission',
            output=complete_file,
            format='json',
            indent=2,
            verbosity=0
        )
        
        if os.path.exists(complete_file):
            size = os.path.getsize(complete_file)
            size_mb = size / (1024 * 1024)
            print(f"   ✓ Sistema completo: {complete_file} ({size_mb:.2f} MB)")
        
    except Exception as e:
        print(f"   ✗ Error en fixture completo: {str(e)}")
    
    # Crear archivo de información
    create_info_file(fixtures_dir, timestamp)
    
    print(f"\n🎉 FIXTURES CREADOS EN: {fixtures_dir}/")
    print(f"📅 Versión: {timestamp}")
    print("\n📋 PARA CARGAR:")
    print(f"   python manage.py loaddata {complete_file}")
    print("   O usar: python manage.py create_system_fixtures")

def create_info_file(fixtures_dir, timestamp):
    """Crear archivo con información de los fixtures"""
    
    info_content = f"""# FIXTURES DEL SISTEMA DE ABERTURAS
Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Versión: {timestamp}

## CONTENIDO

### 01_product_templates_{timestamp}.json
- 111 plantillas de productos base
- Líneas: A30, A40, Modena, Rotonda 640
- Categorías: Ventanas, Puertas, Paños Fijos, etc.

### 02_template_attributes_{timestamp}.json  
- Atributos de configuración
- Línea, Marco, Hoja, Interior
- Opciones condicionales

### 03_attribute_options_{timestamp}.json
- 229 configuraciones de marco
- 421 tipos de hoja  
- 480 tipos de interior
- Relaciones jerárquicas

### 04_products_{timestamp}.json
- Productos del sistema original
- Compatibilidad con sistema anterior

### 05_pricelists_{timestamp}.json
- Listas de precios activas
- Configuraciones de pricing
- Múltiples modos de cálculo

### 06_clientes_{timestamp}.json
- Base de datos de clientes
- Información de contacto
- Estados activos/inactivos

### 07_presupuestos_{timestamp}.json
- Presupuestos de ejemplo
- Configuraciones de plantillas
- Cálculos automáticos

### 08_auth_{timestamp}.json
- Usuarios del sistema
- Grupos y permisos
- Configuración de acceso

### sistema_completo_{timestamp}.json
- Fixture completo con todos los datos
- Listo para restauración completa
- Incluye todas las relaciones

## COMANDOS DE CARGA

### Cargar fixture completo:
```bash
python manage.py loaddata fixtures/sistema_completo_{timestamp}.json
```

### Cargar fixtures individuales:
```bash
python manage.py loaddata fixtures/01_product_templates_{timestamp}.json
python manage.py loaddata fixtures/02_template_attributes_{timestamp}.json
python manage.py loaddata fixtures/03_attribute_options_{timestamp}.json
# ... etc
```

### Usar comando personalizado:
```bash
python manage.py create_system_fixtures
python manage.py load_system_fixtures --complete
```

## BACKUP DE BASE DE DATOS

### Crear backup completo:
```bash
python manage.py backup_database --include-data
```

### Solo estructura:
```bash
python manage.py backup_database
```

## NOTAS

- Los fixtures incluyen toda la información base del sistema
- Compatible con Django fixtures estándar
- Mantiene integridad referencial
- Incluye datos de prueba y configuración
"""
    
    info_file = f'{fixtures_dir}/README_{timestamp}.md'
    
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    print(f"   ✓ Información: {info_file}")

if __name__ == '__main__':
    create_fixtures()