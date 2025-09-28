from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import User, Role
from apps.crm.models import Customer, Address, Contact, PaymentTerm, CustomerTag
from apps.catalog.models import ProductCategory, UoM, TaxRate, Product, PriceList, PriceListRule
from decimal import Decimal

class Command(BaseCommand):
    help = 'Carga datos de ejemplo en el sistema'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('🚀 Cargando datos de ejemplo...')
            
            # Términos de pago
            self.create_payment_terms()
            
            # Etiquetas de clientes
            self.create_customer_tags()
            
            # Unidades de medida
            self.create_uoms()
            
            # Categorías de productos
            self.create_categories()
            
            # Tasas de impuestos
            self.create_tax_rates()
            
            # Productos
            self.create_products()
            
            # Listas de precios
            self.create_price_lists()
            
            # Clientes
            self.create_customers()
            
            self.stdout.write(self.style.SUCCESS('✅ Datos de ejemplo cargados exitosamente'))

    def create_payment_terms(self):
        terms = [
            {'name': 'Contado', 'days': 0, 'early_discount_pct': 0},
            {'name': '30 días', 'days': 30, 'early_discount_pct': 2},
            {'name': '60 días', 'days': 60, 'early_discount_pct': 0},
            {'name': '90 días', 'days': 90, 'early_discount_pct': 0},
        ]
        
        for term_data in terms:
            PaymentTerm.objects.get_or_create(
                name=term_data['name'],
                defaults=term_data
            )
        self.stdout.write('📋 Términos de pago creados')

    def create_customer_tags(self):
        tags = [
            {'name': 'VIP', 'color': '#FFD700'},
            {'name': 'Mayorista', 'color': '#32CD32'},
            {'name': 'Minorista', 'color': '#87CEEB'},
            {'name': 'Moroso', 'color': '#FF6347'},
            {'name': 'Nuevo', 'color': '#9370DB'},
        ]
        
        for tag_data in tags:
            CustomerTag.objects.get_or_create(
                name=tag_data['name'],
                defaults=tag_data
            )
        self.stdout.write('🏷️ Etiquetas de clientes creadas')

    def create_uoms(self):
        uoms = [
            {'code': 'UN', 'name': 'Unidad', 'category': 'unit'},
            {'code': 'M2', 'name': 'Metro cuadrado', 'category': 'area'},
            {'code': 'ML', 'name': 'Metro lineal', 'category': 'length'},
            {'code': 'KG', 'name': 'Kilogramo', 'category': 'weight'},
        ]
        
        for uom_data in uoms:
            UoM.objects.get_or_create(
                code=uom_data['code'],
                defaults=uom_data
            )
        self.stdout.write('📏 Unidades de medida creadas')

    def create_categories(self):
        categories = [
            {'name': 'Ventanas', 'code': 'ventanas'},
            {'name': 'Puertas', 'code': 'puertas'},
            {'name': 'Portones', 'code': 'portones'},
            {'name': 'Accesorios', 'code': 'accesorios'},
            {'name': 'Herrajes', 'code': 'herrajes'},
        ]
        
        for cat_data in categories:
            ProductCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults=cat_data
            )
        self.stdout.write('📦 Categorías de productos creadas')

    def create_tax_rates(self):
        taxes = [
            {'name': 'IVA 21%', 'rate': Decimal('21.00'), 'is_default': True},
            {'name': 'IVA 10.5%', 'rate': Decimal('10.50'), 'is_default': False},
            {'name': 'Exento', 'rate': Decimal('0.00'), 'is_default': False},
        ]
        
        for tax_data in taxes:
            TaxRate.objects.get_or_create(
                name=tax_data['name'],
                defaults=tax_data
            )
        self.stdout.write('💰 Tasas de impuestos creadas')

    def create_products(self):
        ventanas_cat = ProductCategory.objects.get(code='ventanas')
        puertas_cat = ProductCategory.objects.get(code='puertas')
        uom_m2 = UoM.objects.get(code='M2')
        uom_un = UoM.objects.get(code='UN')
        tax_21 = TaxRate.objects.get(name='IVA 21%')
        
        products = [
            {
                'sku': 'VEN-ALU-COR-001',
                'name': 'Ventana Aluminio Corrediza 150x110',
                'category': ventanas_cat,
                'uom': uom_m2,
                'material': 'ALUMINIO',
                'opening_type': 'CORREDIZA',
                'glass_type': 'DVH',
                'width_mm': 1500,
                'height_mm': 1100,
                'tax': tax_21,
                'pricing_method': 'AREA',
                'price_per_m2': Decimal('45000.00'),
                'min_area_m2': Decimal('1.65'),
            },
            {
                'sku': 'VEN-PVC-BAT-001',
                'name': 'Ventana PVC Batiente 120x100',
                'category': ventanas_cat,
                'uom': uom_m2,
                'material': 'PVC',
                'opening_type': 'BATIENTE',
                'glass_type': 'DVH',
                'width_mm': 1200,
                'height_mm': 1000,
                'tax': tax_21,
                'pricing_method': 'AREA',
                'price_per_m2': Decimal('52000.00'),
                'min_area_m2': Decimal('1.20'),
            },
            {
                'sku': 'PTA-ALU-BAT-001',
                'name': 'Puerta Aluminio Batiente 80x200',
                'category': puertas_cat,
                'uom': uom_un,
                'material': 'ALUMINIO',
                'opening_type': 'BATIENTE',
                'glass_type': 'SIMPLE',
                'width_mm': 800,
                'height_mm': 2000,
                'tax': tax_21,
                'pricing_method': 'FIXED',
                'base_price': Decimal('85000.00'),
            },
        ]
        
        for prod_data in products:
            Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults=prod_data
            )
        self.stdout.write('🪟 Productos creados')

    def create_price_lists(self):
        price_list, created = PriceList.objects.get_or_create(
            name='Lista General',
            defaults={
                'currency': 'ARS',
                'is_default': True,
            }
        )
        
        if created:
            # Crear reglas para algunos productos
            products = Product.objects.all()[:2]
            for product in products:
                PriceListRule.objects.create(
                    price_list=price_list,
                    product=product,
                    discount_pct=Decimal('5.00')
                )
        
        self.stdout.write('💲 Listas de precios creadas')

    def create_customers(self):
        vip_tag = CustomerTag.objects.get(name='VIP')
        mayorista_tag = CustomerTag.objects.get(name='Mayorista')
        contado_term = PaymentTerm.objects.get(name='Contado')
        term_30 = PaymentTerm.objects.get(name='30 días')
        
        customers_data = [
            {
                'type': 'EMPRESA',
                'name': 'Constructora San Martín S.A.',
                'tax_id': '30-12345678-9',
                'email': 'ventas@constructorasanmartin.com',
                'phone': '+54 11 4567-8901',
                'credit_limit': Decimal('500000.00'),
                'status': 'ACTIVO',
                'payment_terms': term_30,
                'tags': [mayorista_tag],
                'addresses': [
                    {
                        'kind': 'FACTURACION',
                        'street': 'Av. San Martín',
                        'number': '1234',
                        'city': 'Buenos Aires',
                        'province': 'CABA',
                        'postal_code': '1425',
                        'is_default': True,
                    }
                ],
                'contacts': [
                    {
                        'first_name': 'Juan',
                        'last_name': 'Pérez',
                        'email': 'jperez@constructorasanmartin.com',
                        'phone': '+54 11 4567-8902',
                        'role': 'Gerente de Compras',
                        'is_primary': True,
                    }
                ]
            },
            {
                'type': 'PERSONA',
                'name': 'María González',
                'tax_id': '27-87654321-3',
                'email': 'maria.gonzalez@email.com',
                'phone': '+54 11 9876-5432',
                'credit_limit': Decimal('50000.00'),
                'status': 'ACTIVO',
                'payment_terms': contado_term,
                'tags': [vip_tag],
                'addresses': [
                    {
                        'kind': 'FACTURACION',
                        'street': 'Rivadavia',
                        'number': '5678',
                        'city': 'La Plata',
                        'province': 'Buenos Aires',
                        'postal_code': '1900',
                        'is_default': True,
                    }
                ]
            },
            {
                'type': 'EMPRESA',
                'name': 'Inmobiliaria del Centro',
                'tax_id': '30-98765432-1',
                'email': 'info@inmobiliariacentro.com',
                'phone': '+54 11 2345-6789',
                'credit_limit': Decimal('200000.00'),
                'status': 'POTENCIAL',
                'payment_terms': term_30,
                'addresses': [
                    {
                        'kind': 'FACTURACION',
                        'street': 'Florida',
                        'number': '900',
                        'city': 'Buenos Aires',
                        'province': 'CABA',
                        'postal_code': '1005',
                        'is_default': True,
                    }
                ]
            }
        ]
        
        for customer_data in customers_data:
            addresses_data = customer_data.pop('addresses', [])
            contacts_data = customer_data.pop('contacts', [])
            tags_data = customer_data.pop('tags', [])
            
            customer, created = Customer.objects.get_or_create(
                tax_id=customer_data['tax_id'],
                defaults=customer_data
            )
            
            if created:
                # Agregar tags
                for tag in tags_data:
                    customer.tags.add(tag)
                
                # Crear direcciones
                for addr_data in addresses_data:
                    Address.objects.create(customer=customer, **addr_data)
                
                # Crear contactos
                for contact_data in contacts_data:
                    Contact.objects.create(customer=customer, **contact_data)
        
        self.stdout.write('👥 Clientes creados')