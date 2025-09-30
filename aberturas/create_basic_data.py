#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aberturas.settings.dev')
django.setup()

from apps.catalog.models import MedidaProducto, ColorProducto, LineaProducto, TasaImpuesto, CategoriaProducto

# Crear datos básicos
MedidaProducto.objects.get_or_create(id=1, defaults={'name': 'Estándar', 'code': 'STD'})
ColorProducto.objects.get_or_create(id=1, defaults={'name': 'Blanco', 'code': 'BLA'})  
LineaProducto.objects.get_or_create(id=1, defaults={'name': 'Básica', 'code': 'BAS'})
TasaImpuesto.objects.get_or_create(id=1, defaults={'name': 'IVA 21%', 'rate': 21.00, 'is_default': True})
CategoriaProducto.objects.get_or_create(id=1, defaults={'name': 'General', 'code': 'general'})

print("Datos básicos creados exitosamente")