#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aberturas.settings.dev')
django.setup()

# Ya no hay modelo UnidadMedida
print('No hay unidades de medida para crear - modelo eliminado')