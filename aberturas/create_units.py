#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aberturas.settings.dev')
django.setup()

from apps.catalog.models import UnidadMedida

# Crear más unidades de medida
unidades = [
    ('CM', 'Centímetro', 'length'),
    ('MM', 'Milímetro', 'length'),
    ('M', 'Metro', 'length'),
    ('M3', 'Metro Cúbico', 'area'),
    ('LT', 'Litro', 'unit'),
    ('GR', 'Gramo', 'weight'),
    ('TON', 'Tonelada', 'weight'),
    ('PAR', 'Par', 'unit'),
    ('JGO', 'Juego', 'unit'),
    ('PZA', 'Pieza', 'unit'),
    ('KIT', 'Kit', 'unit'),
    ('SET', 'Set', 'unit')
]

for code, name, category in unidades:
    UnidadMedida.objects.get_or_create(code=code, defaults={'name': name, 'category': category})

print('✅ Unidades de medida creadas exitosamente')