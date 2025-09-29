from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.catalog.models import UoM, ProductCategory, TaxRate, PriceList, Product, PriceListRule
from apps.core.models import Currency


class Command(BaseCommand):
    help = 'Crea datos de prueba para el catálogo'

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
            currency, created = Currency.objects.get_or_create(
                code=currency_data['code'],
                defaults=currency_data
            )
            if created:
                self.stdout.write(f'Moneda creada: {currency}')

        # Crear UoMs
        uoms_data = [
            {'code': 'UN', 'name': 'Unidad', 'category': 'unit'},
            {'code': 'M2', 'name': 'Metro Cuadrado', 'category': 'area'},
            {'code': 'ML', 'name': 'Metro Lineal', 'category': 'length'},
            {'code': 'KG', 'name': 'Kilogramo', 'category': 'weight'},
        ]
        
        for uom_data in uoms_data:
            uom, created = UoM.objects.get_or_create(
                code=uom_data['code'],
                defaults=uom_data
            )
            if created:
                self.stdout.write(f'UoM creado: {uom}')

        # Crear categorías
        categories_data = [
            {'name': 'Ventanas', 'code': 'ventanas'},
            {'name': 'Puertas', 'code': 'puertas'},
            {'name': 'Cerramientos', 'code': 'cerramientos'},
            {'name': 'Accesorios', 'code': 'accesorios'},
        ]
        
        for cat_data in categories_data:
            category, created = ProductCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Categoría creada: {category}')

        # Crear tasas de impuesto
        tax_rates_data = [
            {'name': 'IVA 21%', 'rate': Decimal('21.00'), 'is_default': True},
            {'name': 'IVA 10.5%', 'rate': Decimal('10.50'), 'is_default': False},
            {'name': 'Exento', 'rate': Decimal('0.00'), 'is_default': False},
        ]
        
        for tax_data in tax_rates_data:
            tax, created = TaxRate.objects.get_or_create(
                name=tax_data['name'],
                defaults=tax_data
            )
            if created:
                self.stdout.write(f'Tasa de impuesto creada: {tax}')

        # Crear lista de precios
        price_list, created = PriceList.objects.get_or_create(
            name='Lista General',
            defaults={
                'currency': 'ARS',
                'is_default': True
            }
        )
        if created:
            self.stdout.write(f'Lista de precios creada: {price_list}')

        # Obtener referencias
        uom_un = UoM.objects.get(code='UN')
        uom_m2 = UoM.objects.get(code='M2')
        cat_ventanas = ProductCategory.objects.get(code='ventanas')
        cat_puertas = ProductCategory.objects.get(code='puertas')
        cat_accesorios = ProductCategory.objects.get(code='accesorios')
        tax_21 = TaxRate.objects.get(name='IVA 21%')

        # Crear productos
        products_data = [
            {
                'sku': 'VEN-ALU-COR-001',
                'name': 'Ventana Aluminio Corrediza 120x110',
                'category': cat_ventanas,
                'uom': uom_un,
                'material': 'ALUMINIO',
                'opening_type': 'CORREDIZA',
                'glass_type': 'DVH',
                'color_code': 'BLANCO',
                'width_mm': 1200,
                'height_mm': 1100,
                'weight_kg': Decimal('25.5'),
                'tax': tax_21,
                'pricing_method': 'AREA',
                'base_price': Decimal('0'),
                'price_per_m2': Decimal('45000'),
                'min_area_m2': Decimal('1.00'),
            },
            {
                'sku': 'VEN-PVC-BAT-001',
                'name': 'Ventana PVC Batiente 80x120',
                'category': cat_ventanas,
                'uom': uom_un,
                'material': 'PVC',
                'opening_type': 'BATIENTE',
                'glass_type': 'DVH',
                'color_code': 'BLANCO',
                'width_mm': 800,
                'height_mm': 1200,
                'weight_kg': Decimal('18.2'),
                'tax': tax_21,
                'pricing_method': 'AREA',
                'base_price': Decimal('0'),
                'price_per_m2': Decimal('52000'),
                'min_area_m2': Decimal('0.80'),
            },
            {
                'sku': 'PTA-ALU-BAT-001',
                'name': 'Puerta Aluminio Batiente 80x200',
                'category': cat_puertas,
                'uom': uom_un,
                'material': 'ALUMINIO',
                'opening_type': 'BATIENTE',
                'glass_type': 'SIMPLE',
                'color_code': 'NEGRO',
                'width_mm': 800,
                'height_mm': 2000,
                'weight_kg': Decimal('35.0'),
                'tax': tax_21,
                'pricing_method': 'FIXED',
                'base_price': Decimal('85000'),
                'price_per_m2': Decimal('0'),
                'min_area_m2': Decimal('1.00'),
            },
            {
                'sku': 'ACC-CER-001',
                'name': 'Cerradura Multipunto',
                'category': cat_accesorios,
                'uom': uom_un,
                'material': 'ALUMINIO',
                'opening_type': 'BATIENTE',
                'glass_type': '',
                'color_code': 'CROMADO',
                'width_mm': None,
                'height_mm': None,
                'weight_kg': Decimal('2.5'),
                'tax': tax_21,
                'pricing_method': 'FIXED',
                'base_price': Decimal('15000'),
                'price_per_m2': Decimal('0'),
                'min_area_m2': Decimal('1.00'),
                'is_service': False,
            },
            {
                'sku': 'SRV-INS-001',
                'name': 'Servicio de Instalación',
                'category': cat_accesorios,
                'uom': uom_m2,
                'material': 'ALUMINIO',
                'opening_type': 'CORREDIZA',
                'glass_type': '',
                'color_code': '',
                'width_mm': None,
                'height_mm': None,
                'weight_kg': None,
                'tax': tax_21,
                'pricing_method': 'AREA',
                'base_price': Decimal('0'),
                'price_per_m2': Decimal('8000'),
                'min_area_m2': Decimal('1.00'),
                'is_service': True,
            },
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults=product_data
            )
            if created:
                self.stdout.write(f'Producto creado: {product}')
                
                # Crear regla de precio para la lista general
                rule_data = {
                    'price_list': price_list,
                    'product': product,
                    'method': product.pricing_method,
                    'fixed_price': product.base_price if product.pricing_method == 'FIXED' else None,
                    'price_per_m2': product.price_per_m2 if product.pricing_method == 'AREA' else None,
                    'min_area_m2': product.min_area_m2,
                    'discount_pct': Decimal('0'),
                }
                
                rule, rule_created = PriceListRule.objects.get_or_create(
                    price_list=price_list,
                    product=product,
                    defaults=rule_data
                )
                if rule_created:
                    self.stdout.write(f'  Regla de precio creada: {rule}')

        self.stdout.write(
            self.style.SUCCESS('Datos del catálogo creados exitosamente')
        )