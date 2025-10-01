from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Crear backup completo de la base de datos MySQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Directorio donde guardar el backup'
        )
        parser.add_argument(
            '--include-data',
            action='store_true',
            help='Incluir datos en el backup (por defecto solo estructura)'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        include_data = options['include_data']
        
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Obtener configuración de la base de datos
        db_config = settings.DATABASES['default']
        
        if db_config['ENGINE'] != 'django.db.backends.mysql':
            self.stdout.write(
                self.style.ERROR('Este comando solo funciona con MySQL')
            )
            return
        
        # Configuración de conexión
        host = db_config.get('HOST', 'localhost')
        port = db_config.get('PORT', '3306')
        user = db_config.get('USER', 'root')
        password = db_config.get('PASSWORD', '')
        database = db_config.get('NAME')
        
        # Nombre del archivo de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_type = 'completo' if include_data else 'estructura'
        backup_file = f'{output_dir}/backup_{backup_type}_{timestamp}.sql'
        
        # Comando mysqldump
        cmd = [
            'mysqldump',
            f'--host={host}',
            f'--port={port}',
            f'--user={user}',
            f'--password={password}',
            '--single-transaction',
            '--routines',
            '--triggers',
        ]
        
        if not include_data:
            cmd.append('--no-data')
        
        cmd.append(database)
        
        self.stdout.write(f'Creando backup: {backup_file}')
        
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
            
            # Obtener tamaño del archivo
            file_size = os.path.getsize(backup_file)
            size_mb = file_size / (1024 * 1024)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Backup creado: {backup_file} ({size_mb:.2f} MB)'
                )
            )
            
            # Crear script de restauración
            self.create_restore_script(backup_file, db_config)
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creando backup: {e.stderr}')
            )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('✗ mysqldump no encontrado. Instalar MySQL client.')
            )

    def create_restore_script(self, backup_file, db_config):
        """Crear script para restaurar el backup"""
        
        script_content = f'''#!/bin/bash
# Script de restauración automática
# Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Configuración de la base de datos
HOST="{db_config.get('HOST', 'localhost')}"
PORT="{db_config.get('PORT', '3306')}"
USER="{db_config.get('USER', 'root')}"
PASSWORD="{db_config.get('PASSWORD', '')}"
DATABASE="{db_config.get('NAME')}"

echo "Restaurando backup: {backup_file}"
echo "Base de datos: $DATABASE"
echo "Host: $HOST:$PORT"
echo ""

# Confirmar antes de proceder
read -p "¿Continuar con la restauración? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restauración cancelada"
    exit 1
fi

# Ejecutar restauración
mysql --host="$HOST" --port="$PORT" --user="$USER" --password="$PASSWORD" "$DATABASE" < "{backup_file}"

if [ $? -eq 0 ]; then
    echo "✓ Restauración completada exitosamente"
else
    echo "✗ Error en la restauración"
    exit 1
fi
'''
        
        script_file = backup_file.replace('.sql', '_restore.sh')
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Hacer ejecutable en sistemas Unix
        try:
            os.chmod(script_file, 0o755)
        except:
            pass
        
        self.stdout.write(f'✓ Script de restauración: {script_file}')