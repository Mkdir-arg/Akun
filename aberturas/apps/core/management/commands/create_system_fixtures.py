from django.core.management.base import BaseCommand
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Crear fixtures con toda la información base del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='fixtures',
            help='Directorio donde guardar los fixtures'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        self.stdout.write(self.style.SUCCESS('Creando fixtures del sistema base...'))
        
        # Lista de modelos a exportar con sus archivos
        fixtures_config = [
            # Catálogo - Información base
            {
                'models': ['catalog.ProductTemplate'],
                'file': f'{output_dir}/01_product_templates.json',
                'description': 'Plantillas de productos (111 productos base)'
            },
            {
                'models': ['catalog.TemplateAttribute'],
                'file': f'{output_dir}/02_template_attributes.json',
                'description': 'Atributos de plantillas (línea, marco, hoja, interior)'
            },
            {
                'models': ['catalog.AttributeOption'],
                'file': f'{output_dir}/03_attribute_options.json',
                'description': 'Opciones de atributos (229 marcos, 421 hojas, 480 interiores)'
            },
            
            # Productos originales
            {
                'models': ['catalog.Product'],
                'file': f'{output_dir}/04_products.json',
                'description': 'Productos originales del sistema'
            },
            {
                'models': ['catalog.PriceList', 'catalog.PriceListItem'],
                'file': f'{output_dir}/05_pricelists.json',
                'description': 'Listas de precios y sus ítems'
            },
            
            # CRM
            {
                'models': ['crm.Cliente'],
                'file': f'{output_dir}/06_clientes.json',
                'description': 'Clientes del sistema'
            },
            
            # Ventas (ejemplos)
            {
                'models': ['sales.Presupuesto', 'sales.LineaPresupuesto'],
                'file': f'{output_dir}/07_presupuestos.json',
                'description': 'Presupuestos de ejemplo'
            },
            
            # Usuarios y permisos
            {
                'models': ['auth.User', 'auth.Group'],
                'file': f'{output_dir}/08_users_groups.json',
                'description': 'Usuarios y grupos del sistema'
            },
            
            # Configuración del sistema
            {
                'models': ['core.SystemConfig'],
                'file': f'{output_dir}/09_system_config.json',
                'description': 'Configuración del sistema'
            }
        ]
        
        # Generar cada fixture
        for config in fixtures_config:
            try:
                self.stdout.write(f"Generando: {config['description']}")
                
                call_command(
                    'dumpdata',
                    *config['models'],
                    output=config['file'],
                    format='json',
                    indent=2
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Creado: {config['file']}")
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"⚠ Error en {config['file']}: {str(e)}")
                )
        
        # Crear fixture completo
        self.stdout.write('\nCreando fixture completo del sistema...')
        
        try:
            call_command(
                'dumpdata',
                '--exclude=contenttypes',
                '--exclude=sessions',
                '--exclude=admin.logentry',
                output=f'{output_dir}/sistema_completo.json',
                format='json',
                indent=2
            )
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ Fixture completo: {output_dir}/sistema_completo.json")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Error en fixture completo: {str(e)}")
            )
        
        # Crear script de carga
        self.create_load_script(output_dir)
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Fixtures creados en: {output_dir}/')
        )
        self.stdout.write('Para cargar: python manage.py load_system_fixtures')

    def create_load_script(self, output_dir):
        """Crear comando para cargar fixtures"""
        
        load_script = f'''from django.core.management.base import BaseCommand
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Cargar fixtures del sistema base'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fixtures-dir',
            type=str,
            default='{output_dir}',
            help='Directorio con los fixtures'
        )
        parser.add_argument(
            '--complete',
            action='store_true',
            help='Cargar fixture completo en lugar de individuales'
        )

    def handle(self, *args, **options):
        fixtures_dir = options['fixtures_dir']
        
        if options['complete']:
            # Cargar fixture completo
            fixture_file = os.path.join(fixtures_dir, 'sistema_completo.json')
            if os.path.exists(fixture_file):
                self.stdout.write('Cargando fixture completo...')
                call_command('loaddata', fixture_file)
                self.stdout.write(self.style.SUCCESS('✓ Sistema cargado completamente'))
            else:
                self.stdout.write(self.style.ERROR('✗ No se encontró sistema_completo.json'))
            return
        
        # Cargar fixtures individuales en orden
        fixtures_order = [
            '01_product_templates.json',
            '02_template_attributes.json', 
            '03_attribute_options.json',
            '04_products.json',
            '05_pricelists.json',
            '06_clientes.json',
            '07_presupuestos.json',
            '08_users_groups.json',
            '09_system_config.json'
        ]
        
        self.stdout.write('Cargando fixtures individuales...')
        
        for fixture_name in fixtures_order:
            fixture_path = os.path.join(fixtures_dir, fixture_name)
            
            if os.path.exists(fixture_path):
                try:
                    self.stdout.write(f'Cargando: {{fixture_name}}')
                    call_command('loaddata', fixture_path)
                    self.stdout.write(self.style.SUCCESS(f'✓ {{fixture_name}}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠ Error en {{fixture_name}}: {{str(e)}}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠ No encontrado: {{fixture_name}}'))
        
        self.stdout.write(self.style.SUCCESS('\\n🎉 Fixtures cargados'))
'''
        
        script_path = 'apps/core/management/commands/load_system_fixtures.py'
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(load_script)
        
        self.stdout.write(f"✓ Script de carga creado: {script_path}")