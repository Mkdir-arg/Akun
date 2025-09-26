from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.catalog.models import UoM, TaxRate, ProductCategory, Product, PriceList, PriceListRule


class Command(BaseCommand):
    help = 'Crea datos de prueba para el catálogo'

    def handle(self, *args, **options):
        # Crear UoM
        uoms_data = [
            ('u', 'Unidad', 'unit'),
            ('mm', 'Milímetro', 'length'),
            ('m2', 'Metro cuadrado', 'area'),
            ('kg', 'Kilogramo', 'weight'),
        ]
        
        for code, name, category in uoms_data:
            uom, created = UoM.objects.get_or_create(
                code=code,
                defaults={'name': name, 'category': category}
            )
            if created:
                self.stdout.write(f'UoM creado: {uom}')

        # Crear tasas de impuesto
        taxes_data = [
            ('IVA 21%', Decimal('21.00'), True),
            ('IVA 10.5%', Decimal('10.50'), False),
            ('Exento 0%', Decimal('0.00'), False),
        ]
        
        for name, rate, is_default in taxes_data:
            tax, created = TaxRate.objects.get_or_create(
                name=name,
                defaults={'rate': rate, 'is_default': is_default}
            )
            if created:
                self.stdout.write(f'Tasa de impuesto creada: {tax}')

        # Crear categorías
        categories_data = [
            ('Aberturas', 'aberturas', None),
            ('Ventanas', 'ventanas', 'aberturas'),
            ('Puertas', 'puertas', 'aberturas'),
            ('Servicios', 'servicios', None),
        ]
        
        category_objects = {}
        for name, code, parent_code in categories_data:
            parent = category_objects.get(parent_code) if parent_code else None
            category, created = ProductCategory.objects.get_or_create(
                code=code,
                defaults={'name': name, 'parent': parent}
            )
            category_objects[code] = category
            if created:
                self.stdout.write(f'Categoría creada: {category}')

        # Crear lista de precios por defecto
        price_list, created = PriceList.objects.get_or_create(
            name='Lista Mayorista',
            defaults={'currency': 'ARS', 'is_default': True}
        )
        if created:
            self.stdout.write(f'Lista de precios creada: {price_list}')

        # Obtener objetos necesarios
        uom_u = UoM.objects.get(code='u')
        tax_21 = TaxRate.objects.get(name='IVA 21%')
        cat_ventanas = category_objects['ventanas']
        cat_puertas = category_objects['puertas']
        cat_servicios = category_objects['servicios']

        # Crear productos demo
        products_data = [
            {
                'sku': 'VC-ALU-2H',
                'name': 'Ventana corrediza aluminio 2 hojas',
                'category': cat_ventanas,
                'material': 'ALUMINIO',
                'opening_type': 'CORREDIZA',
                'glass_type': 'DVH',
                'pricing_method': 'AREA',
                'price_per_m2': Decimal('85000.00'),
                'min_area_m2': Decimal('1.20'),
            },
            {
                'sku': 'PB-PVC',
                'name': 'Puerta batiente PVC',
                'category': cat_puertas,
                'material': 'PVC',
                'opening_type': 'BATIENTE',
                'glass_type': 'SIMPLE',
                'pricing_method': 'AREA',
                'price_per_m2': Decimal('110000.00'),
                'min_area_m2': Decimal('1.50'),
            },
            {
                'sku': 'INST',
                'name': 'Servicio de instalación',
                'category': cat_servicios,
                'material': 'ALUMINIO',  # Requerido por el modelo
                'opening_type': 'PAÑO_FIJO',  # Requerido por el modelo
                'pricing_method': 'FIXED',
                'base_price': Decimal('45000.00'),
                'is_service': True,
            },
        ]

        created_products = []
        for product_data in products_data:
            product_data.update({
                'uom': uom_u,
                'tax': tax_21,
            })
            
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults=product_data
            )
            created_products.append(product)
            if created:
                self.stdout.write(f'Producto creado: {product}')

        # Crear reglas de precio demo
        rules_data = [
            {
                'product': created_products[0],  # VC-ALU-2H
                'method': 'AREA',
                'price_per_m2': Decimal('82000.00'),  # Precio especial en lista
                'discount_pct': Decimal('5.00'),
            },
            {
                'product': created_products[1],  # PB-PVC
                'method': 'AREA',
                'price_per_m2': Decimal('105000.00'),
                'discount_pct': Decimal('3.00'),
            },
            {
                'product': created_products[2],  # INST
                'method': 'FIXED',
                'fixed_price': Decimal('42000.00'),
                'discount_pct': Decimal('0.00'),
            },
        ]

        for rule_data in rules_data:
            rule_data['price_list'] = price_list
            
            rule, created = PriceListRule.objects.get_or_create(
                price_list=price_list,
                product=rule_data['product'],
                defaults=rule_data
            )
            if created:
                self.stdout.write(f'Regla de precio creada: {rule}')

        self.stdout.write(
            self.style.SUCCESS('Datos de catálogo creados exitosamente')
        )