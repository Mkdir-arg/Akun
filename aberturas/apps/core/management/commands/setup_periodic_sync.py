from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = "Configura sincronización periódica de plantillas legacy"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra lo que haría sin ejecutar',
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Limpia cache antes de sincronizar',
        )

    def handle(self, *args, **options):
        if options['clear_cache']:
            cache.clear()
            self.stdout.write(self.style.SUCCESS("Cache limpiado"))

        if options['dry_run']:
            self.stdout.write("=== MODO DRY RUN ===")
            self.stdout.write("Se ejecutaría: sync_templates_from_legacy")
            self.stdout.write("Configuración sugerida para cron:")
            self.stdout.write("# Sincronizar plantillas legacy cada 6 horas")
            self.stdout.write("0 */6 * * * cd /path/to/project && python manage.py sync_templates_from_legacy")
            return

        # Ejecutar sincronización
        from django.core.management import call_command
        
        self.stdout.write("Iniciando sincronización de plantillas legacy...")
        call_command('sync_templates_from_legacy')
        self.stdout.write(self.style.SUCCESS("Sincronización completada"))