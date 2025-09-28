from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import User, Role
from apps.crm.models import Customer, Address, Contact, PaymentTerm, CustomerTag
from apps.catalog.models import ProductCategory, UoM, TaxRate, Product, PriceList, PriceListRule
from decimal import Decimal

class Command(BaseCommand):
    help = 'Configura el sistema completo con datos iniciales'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('🚀 Configurando sistema completo...')
            
            # Crear superusuario
            self.create_superuser()
            
            # Crear roles
            self.create_roles()
            
            # Cargar datos del catálogo
            self.create_payment_terms()
            self.create_customer_tags()
            self.create_uoms()
            self.create_categories()
            self.create_tax_rates()
            self.create_products()
            self.create_price_lists()
            
            # Cargar clientes
            self.create_customers()
            
            self.stdout.write(self.style.SUCCESS('✅ Sistema configurado exitosamente'))

    def create_superuser(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@admin.com', 'admin123')
            self.stdout.write('👤 Superusuario admin creado')
        else:
            self.stdout.write('👤 Superusuario admin ya existe')

    def create_roles(self):
        roles_data = [
            {
                'name': 'Administrador',
                'description': 'Acceso completo al sistema',
                'can_access_crm': True,
                'can_access_catalog': True,
                'can_access_orders': True,
                'can_access_quotes': True,
                'can_access_reports': True,
                'can_access_settings': True,
                'can_create': True,
                'can_edit': True,
                'can_delete': True,
                'can_export': True,
            },
            {
                'name': 'Ventas',
                'description': 'Gestión de clientes y pedidos',
                'can_access_crm': True,
                'can_access_catalog': True,
                'can_access_orders': True,
                'can_access_quotes': True,
                'can_create': True,
                'can_edit': True,
            },
            {
                'name': 'Depósito',
                'description': 'Control de inventario',
                'can_access_catalog': True,
                'can_access_orders': True,
                'can_create': True,
                'can_edit': True,
            }
        ]
        
        for role_data in roles_data:
            Role.objects.get_or_create(name=role_data['name'], defaults=role_data)
        self.stdout.write('👥 Roles creados')

    def create_payment_terms(self):
        terms = [
            {'name': 'Contado', 'days': 0, 'early_discount_pct': 0},
            {'name': '30 días', 'days': 30, 'early_discount_pct': 2},
            {'name': '60 días', 'days': 60, 'early_discount_pct': 0},
            {'name': '90 días', 'days': 90, 'early_discount_pct': 0},
        ]
        
        for term_data in terms:
            PaymentTerm.objects.get_or_create(name=term_data['name'], defaults=term_data)
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
            CustomerTag.objects.get_or_create(name=tag_data['name'], defaults=tag_data)
        self.stdout.write('🏷️ Etiquetas de clientes creadas')

    def create_uoms(self):
        uoms = [
            {'code': 'UN', 'name': 'Unidad', 'category': 'unit'},
            {'code': 'M2', 'name': 'Metro cuadrado', 'category': 'area'},
            {'code': 'ML', 'name': 'Metro lineal', 'category': 'length'},
            {'code': 'KG', 'name': 'Kilogramo', 'category': 'weight'},
        ]
        
        for uom_data in uoms:
            UoM.objects.get_or_create(code=uom_data['code'], defaults=uom_data)
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
            ProductCategory.objects.get_or_create(code=cat_data['code'], defaults=cat_data)
        self.stdout.write('📦 Categorías de productos creadas')

    def create_tax_rates(self):
        taxes = [
            {'name': 'IVA 21%', 'rate': Decimal('21.00'), 'is_default': True},
            {'name': 'IVA 10.5%', 'rate': Decimal('10.50'), 'is_default': False},
            {'name': 'Exento', 'rate': Decimal('0.00'), 'is_default': False},
        ]
        
        for tax_data in taxes:
            TaxRate.objects.get_or_create(name=tax_data['name'], defaults=tax_data)
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
                'subcategory': 'CORREDIZA_DOBLE',
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
                'subcategory': 'BATIENTE_SIMPLE',
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
                'subcategory': 'ENTRADA_PRINCIPAL',
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
            Product.objects.get_or_create(sku=prod_data['sku'], defaults=prod_data)
        self.stdout.write('🪟 Productos creados')

    def create_price_lists(self):
        price_list, created = PriceList.objects.get_or_create(
            name='Lista General',
            defaults={'currency': 'ARS', 'is_default': True}
        )
        
        if created:
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
            },
        ]
        
        for customer_data in customers_data:
            tags_data = customer_data.pop('tags', [])
            customer, created = Customer.objects.get_or_create(
                tax_id=customer_data['tax_id'],
                defaults=customer_data
            )
            if created:
                for tag in tags_data:
                    customer.tags.add(tag)
        
        self.stdout.write('👥 Clientes creados')