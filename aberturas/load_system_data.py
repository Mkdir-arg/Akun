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
from apps.crm.models import TerminoPago, EtiquetaCliente

# Monedas
Moneda.objects.get_or_create(code='ARS', defaults={'name': 'Peso Argentino', 'symbol': '$', 'is_default': True})
Moneda.objects.get_or_create(code='USD', defaults={'name': 'Dólar Estadounidense', 'symbol': 'US$'})

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

print('✅ Data del sistema cargada exitosamente (sin productos ni categorías)')