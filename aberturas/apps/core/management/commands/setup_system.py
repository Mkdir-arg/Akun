from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Configura el sistema con todos los datos iniciales necesarios'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Configurando sistema...')
        
        try:
            # Ejecutar seed_catalog que incluye las monedas
            self.stdout.write('📦 Cargando catálogo y monedas...')
            call_command('seed_catalog')
            
            self.stdout.write(
                self.style.SUCCESS('✅ Sistema configurado exitosamente')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error configurando sistema: {e}')
            )