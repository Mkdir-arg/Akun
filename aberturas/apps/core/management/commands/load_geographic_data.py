import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.core.models import Provincia, Municipio


class Command(BaseCommand):
    help = 'Load geographic data from fixtures'

    def handle(self, *args, **options):
        fixture_path = os.path.join(settings.BASE_DIR, 'fixtures', 'localidad_municipio_provincia.json')
        
        if not os.path.exists(fixture_path):
            self.stdout.write(
                self.style.ERROR(f'Fixture file not found: {fixture_path}')
            )
            return

        with open(fixture_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Cargar provincias
        provincias_created = 0
        municipios_created = 0

        for item in data:
            if item['model'] == 'core.provincia':
                provincia, created = Provincia.objects.get_or_create(
                    id=item['pk'],
                    defaults={'nombre': item['fields']['nombre']}
                )
                if created:
                    provincias_created += 1

        # Cargar municipios
        for item in data:
            if item['model'] == 'core.municipio':
                try:
                    provincia = Provincia.objects.get(id=item['fields']['provincia'])
                    municipio, created = Municipio.objects.get_or_create(
                        id=item['pk'],
                        defaults={
                            'nombre': item['fields']['nombre'],
                            'provincia': provincia
                        }
                    )
                    if created:
                        municipios_created += 1
                except Provincia.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Provincia {item["fields"]["provincia"]} not found for municipio {item["fields"]["nombre"]}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded {provincias_created} provincias and {municipios_created} municipios'
            )
        )