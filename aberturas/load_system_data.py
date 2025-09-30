#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aberturas.settings.dev')
django.setup()

from apps.accounts.models import Role
from apps.core.models import Moneda
from apps.catalog.models import CategoriaProducto, TasaImpuesto, UnidadMedida, ListaPrecios
from apps.crm.models import TerminoPago, EtiquetaCliente

# Monedas
Moneda.objects.get_or_create(code='ARS', defaults={'name': 'Peso Argentino', 'symbol': '$', 'is_default': True})
Moneda.objects.get_or_create(code='USD', defaults={'name': 'Dólar Estadounidense', 'symbol': 'US$'})

# Unidades de medida
UnidadMedida.objects.get_or_create(code='UN', defaults={'name': 'Unidad', 'category': 'unit'})
UnidadMedida.objects.get_or_create(code='M2', defaults={'name': 'Metro Cuadrado', 'category': 'area'})
UnidadMedida.objects.get_or_create(code='ML', defaults={'name': 'Metro Lineal', 'category': 'length'})
UnidadMedida.objects.get_or_create(code='KG', defaults={'name': 'Kilogramo', 'category': 'weight'})

# Categorías
CategoriaProducto.objects.get_or_create(name='Ventanas', defaults={'code': 'ventanas'})
CategoriaProducto.objects.get_or_create(name='Puertas', defaults={'code': 'puertas'})
CategoriaProducto.objects.get_or_create(name='Cerramientos', defaults={'code': 'cerramientos'})
CategoriaProducto.objects.get_or_create(name='Accesorios', defaults={'code': 'accesorios'})

# Tasas de impuesto
TasaImpuesto.objects.get_or_create(name='IVA 21%', defaults={'rate': 21.00, 'is_default': True})
TasaImpuesto.objects.get_or_create(name='IVA 10.5%', defaults={'rate': 10.50})
TasaImpuesto.objects.get_or_create(name='Exento', defaults={'rate': 0.00})

# Lista de precios
ListaPrecios.objects.get_or_create(name='Lista General', defaults={'currency': 'ARS', 'is_default': True})

# Términos de pago
TerminoPago.objects.get_or_create(name='Contado', defaults={'days': 0})
TerminoPago.objects.get_or_create(name='15 días', defaults={'days': 15})
TerminoPago.objects.get_or_create(name='30 días', defaults={'days': 30})
TerminoPago.objects.get_or_create(name='60 días', defaults={'days': 60})

# Etiquetas de cliente
EtiquetaCliente.objects.get_or_create(name='Mayorista', defaults={'color': '#3B82F6'})
EtiquetaCliente.objects.get_or_create(name='Obra', defaults={'color': '#10B981'})
EtiquetaCliente.objects.get_or_create(name='Premium', defaults={'color': '#F59E0B'})
EtiquetaCliente.objects.get_or_create(name='Moroso', defaults={'color': '#EF4444'})
EtiquetaCliente.objects.get_or_create(name='VIP', defaults={'color': '#8B5CF6'})

print('✅ Toda la data del sistema cargada exitosamente')