#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aberturas.settings.dev')
    django.setup()
    
    print("🔥 Servidor Django con logs de transacciones en tiempo real")
    print("=" * 60)
    
    # Ejecutar el servidor
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:8000']
    execute_from_command_line(sys.argv)