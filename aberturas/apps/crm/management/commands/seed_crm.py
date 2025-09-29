from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.crm.models import Cliente, Direccion, Contacto, TerminoPago, EtiquetaCliente, NotaCliente
from apps.catalog.models import ListaPrecios
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Crea datos de prueba para CRM'

    def handle(self, *args, **options):
        # Crear términos de pago
        payment_terms = [
            {'name': 'Contado', 'days': 0, 'early_discount_pct': Decimal('2.00')},
            {'name': '15 días', 'days': 15, 'early_discount_pct': Decimal('1.00')},
            {'name': '30 días', 'days': 30, 'early_discount_pct': Decimal('0.00')},
            {'name': '60 días', 'days': 60, 'early_discount_pct': Decimal('0.00')},
        ]
        
        for term_data in payment_terms:
            term, created = TerminoPago.objects.get_or_create(
                name=term_data['name'],
                defaults=term_data
            )
            if created:
                self.stdout.write(f'Término de pago creado: {term}')
        
        # Crear tags
        tags_data = [
            {'name': 'Mayorista', 'color': '#3B82F6'},
            {'name': 'Obra', 'color': '#EF4444'},
            {'name': 'Premium', 'color': '#F59E0B'},
            {'name': 'Moroso', 'color': '#DC2626'},
            {'name': 'VIP', 'color': '#8B5CF6'},
        ]
        
        for tag_data in tags_data:
            tag, created = EtiquetaCliente.objects.get_or_create(
                name=tag_data['name'],
                defaults=tag_data
            )
            if created:
                self.stdout.write(f'Tag creado: {tag}')
        
        # Obtener lista de precios por defecto
        default_price_list = ListaPrecios.objects.filter(is_default=True).first()
        contado = TerminoPago.objects.get(name='Contado')
        dias_30 = TerminoPago.objects.get(name='30 días')
        
        # Obtener tags
        mayorista = EtiquetaCliente.objects.get(name='Mayorista')
        obra = EtiquetaCliente.objects.get(name='Obra')
        premium = EtiquetaCliente.objects.get(name='Premium')
        
        # Obtener usuario admin para notas
        admin_user = User.objects.filter(is_superuser=True).first()

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
                'payment_terms': dias_30,
                'status': 'ACTIVO',
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
                'payment_terms': contado,
                'status': 'ACTIVO',
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
                'payment_terms': dias_30,
                'status': 'ACTIVO',
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
                'payment_terms': contado,
                'status': 'ACTIVO',
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
                'payment_terms': dias_30,
                'status': 'ACTIVO',
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

        for i, customer_data in enumerate(customers_data):
            addresses_data = customer_data.pop('addresses', [])
            
            customer, created = Cliente.objects.get_or_create(
                name=customer_data['name'],
                defaults=customer_data
            )
            
            if created:
                self.stdout.write(f'Cliente creado: {customer}')
                
                # Asignar tags
                if i == 0:  # Constructora
                    customer.tags.add(mayorista, obra)
                elif i == 2:  # Desarrollos
                    customer.tags.add(premium, obra)
                elif i == 4:  # Arquitectura
                    customer.tags.add(premium)
                
                # Crear direcciones
                for address_data in addresses_data:
                    address_data['customer'] = customer
                    address = Direccion.objects.create(**address_data)
                    self.stdout.write(f'  Dirección creada: {address}')
                
                # Crear contactos
                if customer.type == 'EMPRESA':
                    contact = Contacto.objects.create(
                        customer=customer,
                        first_name='Carlos',
                        last_name='Responsable',
                        email=f'contacto@empresa{i}.com',
                        phone='011-1234-5678',
                        role='Compras',
                        is_primary=True
                    )
                    self.stdout.write(f'  Contacto creado: {contact}')
                
                # Crear nota inicial
                if admin_user:
                    note = NotaCliente.objects.create(
                        customer=customer,
                        author=admin_user,
                        body=f'Cliente {customer.type.lower()} creado en el sistema. Revisar documentación y condiciones comerciales.',
                        pinned=True
                    )
                    self.stdout.write(f'  Nota creada: {note}')
            else:
                self.stdout.write(f'Cliente ya existe: {customer}')

        self.stdout.write(
            self.style.SUCCESS('Datos de CRM creados exitosamente')
        )