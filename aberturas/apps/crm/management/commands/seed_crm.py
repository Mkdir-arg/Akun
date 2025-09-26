from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.crm.models import Customer, Address
from apps.catalog.models import PriceList


class Command(BaseCommand):
    help = 'Crea datos de prueba para CRM'

    def handle(self, *args, **options):
        # Obtener lista de precios por defecto
        default_price_list = PriceList.objects.filter(is_default=True).first()

        # Datos de clientes
        customers_data = [
            {
                'type': 'EMPRESA',
                'name': 'Constructora San Martín S.A.',
                'tax_id': '30123456789',
                'email': 'ventas@constructorasanmartin.com.ar',
                'phone': '011-4567-8901',
                'credit_limit': Decimal('500000.00'),
                'default_price_list': default_price_list,
                'addresses': [
                    {
                        'kind': 'FACTURACION',
                        'street': 'Av. San Martín',
                        'number': '1234',
                        'city': 'Buenos Aires',
                        'province': 'CABA',
                        'postal_code': '1425',
                        'is_default': True,
                    },
                    {
                        'kind': 'ENVIO',
                        'street': 'Av. Corrientes',
                        'number': '5678',
                        'city': 'Buenos Aires',
                        'province': 'CABA',
                        'postal_code': '1414',
                        'is_default': True,
                    }
                ]
            },
            {
                'type': 'PERSONA',
                'name': 'Juan Carlos Pérez',
                'tax_id': '20123456781',
                'email': 'jcperez@gmail.com',
                'phone': '011-2345-6789',
                'credit_limit': Decimal('100000.00'),
                'addresses': [
                    {
                        'kind': 'FACTURACION',
                        'street': 'Rivadavia',
                        'number': '9876',
                        'city': 'La Plata',
                        'province': 'Buenos Aires',
                        'postal_code': '1900',
                        'is_default': True,
                    }
                ]
            },
            {
                'type': 'EMPRESA',
                'name': 'Desarrollos Inmobiliarios Norte',
                'tax_id': '30987654321',
                'email': 'compras@dinorte.com.ar',
                'phone': '011-8765-4321',
                'credit_limit': Decimal('750000.00'),
                'default_price_list': default_price_list,
                'addresses': [
                    {
                        'kind': 'FACTURACION',
                        'street': 'Av. del Libertador',
                        'number': '2468',
                        'city': 'Vicente López',
                        'province': 'Buenos Aires',
                        'postal_code': '1638',
                        'is_default': True,
                    }
                ]
            },
            {
                'type': 'PERSONA',
                'name': 'María Elena González',
                'tax_id': '27456789123',
                'email': 'megonzalez@hotmail.com',
                'phone': '011-3456-7890',
                'credit_limit': Decimal('50000.00'),
                'addresses': [
                    {
                        'kind': 'FACTURACION',
                        'street': 'Mitre',
                        'number': '1357',
                        'city': 'San Isidro',
                        'province': 'Buenos Aires',
                        'postal_code': '1642',
                        'is_default': True,
                    },
                    {
                        'kind': 'ENVIO',
                        'street': 'Belgrano',
                        'number': '2468',
                        'city': 'San Isidro',
                        'province': 'Buenos Aires',
                        'postal_code': '1642',
                        'is_default': True,
                    }
                ]
            },
            {
                'type': 'EMPRESA',
                'name': 'Arquitectura & Diseño Moderno',
                'tax_id': '30555666777',
                'email': 'info@admoderno.com.ar',
                'phone': '011-5555-6666',
                'credit_limit': Decimal('300000.00'),
                'addresses': [
                    {
                        'kind': 'FACTURACION',
                        'street': 'Av. Santa Fe',
                        'number': '3691',
                        'city': 'Buenos Aires',
                        'province': 'CABA',
                        'postal_code': '1425',
                        'is_default': True,
                    }
                ]
            }
        ]

        for customer_data in customers_data:
            addresses_data = customer_data.pop('addresses', [])
            
            customer, created = Customer.objects.get_or_create(
                name=customer_data['name'],
                defaults=customer_data
            )
            
            if created:
                self.stdout.write(f'Cliente creado: {customer}')
                
                # Crear direcciones
                for address_data in addresses_data:
                    address_data['customer'] = customer
                    address = Address.objects.create(**address_data)
                    self.stdout.write(f'  Dirección creada: {address}')
            else:
                self.stdout.write(f'Cliente ya existe: {customer}')

        self.stdout.write(
            self.style.SUCCESS('Datos de CRM creados exitosamente')
        )