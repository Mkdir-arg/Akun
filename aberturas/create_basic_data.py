#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aberturas.settings.dev')
django.setup()

# Ya no hay modelos de productos para crear datos básicos
print("No hay datos básicos de productos para crear - solo plantillas disponibles")