from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.core.models import Moneda


class Command(BaseCommand):
    help = 'Crea las monedas iniciales del sistema'

    def handle(self, *args, **options):
        # Crear monedas
        currencies_data = [
            {
                'code': 'USD',
                'name': 'Dólar Estadounidense',
                'symbol': '$',
                'exchange_rate': Decimal('1.00'),
                'is_default': True
            },
            {
                'code': 'ARS',
                'name': 'Peso Argentino',
                'symbol': '$',
                'exchange_rate': Decimal('350.00'),
                'is_default': False
            },
        ]
        
        for currency_data in currencies_data:
            currency, created = Moneda.objects.get_or_create(
                code=currency_data['code'],
                defaults=currency_data
            )
            if created:
                self.stdout.write(f'Moneda creada: {currency}')
            else:
                self.stdout.write(f'Moneda ya existe: {currency}')

        self.stdout.write(
            self.style.SUCCESS('Monedas creadas exitosamente')
        )