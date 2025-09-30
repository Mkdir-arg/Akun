#!/usr/bin/env python
"""
Script para crear plantilla de ejemplo (Ventana Módena)
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aberturas.settings.dev')
django.setup()

from apps.catalog.models import (
    ProductTemplate, TemplateAttribute, AttributeOption, 
    AttributeType, PricingMode, RenderVariant
)

def create_modena_template():
    # Buscar plantilla existente por line_name
    try:
        template = ProductTemplate.objects.get(line_name='Módena')
        print(f"ℹ️ Plantilla ya existe: {template}")
        # Limpiar atributos existentes para recrear
        template.attributes.all().delete()
        # Actualizar campos
        template.code = 'ventana-modena'
        template.base_price_net = 50000.00
        template.save()
        created = False
    except ProductTemplate.DoesNotExist:
        template = ProductTemplate.objects.create(
            product_class='VENTANA',
            line_name='Módena',
            code='ventana-modena',
            base_price_net=50000.00,
            currency='ARS',
            requires_dimensions=True,
            is_active=True,
            version=1
        )
        created = True
        print(f"✅ Plantilla creada: {template}")

    
    # 1. Dimensiones (DIMENSIONS_MM)
    dim_attr = TemplateAttribute.objects.create(
        template=template,
        name='Dimensiones',
        code='dim',
        type=AttributeType.DIMENSIONS_MM,
        is_required=True,
        order=1,
        min_width=500,
        max_width=2400,
        min_height=500,
        max_height=2400,
        step_mm=10
    )
    print(f"✅ Atributo creado: {dim_attr}")
    
    # 2. Hojas (SELECT con FACTOR)
    hojas_attr = TemplateAttribute.objects.create(
        template=template,
        name='Hojas',
        code='hojas',
        type=AttributeType.SELECT,
        is_required=True,
        order=2,
        render_variant=RenderVariant.RADIO
    )
    
    AttributeOption.objects.create(
        attribute=hojas_attr,
        label='1 Hoja',
        code='1h',
        pricing_mode=PricingMode.ABS,
        price_value=Decimal('0'),
        order=1,
        is_default=True
    )
    
    AttributeOption.objects.create(
        attribute=hojas_attr,
        label='2 Hojas',
        code='2h',
        pricing_mode=PricingMode.FACTOR,
        price_value=Decimal('1.85'),
        order=2
    )
    print(f"✅ Atributo creado: {hojas_attr} con 2 opciones")
    
    # 3. Color (SELECT con swatches y FACTOR)
    color_attr = TemplateAttribute.objects.create(
        template=template,
        name='Color',
        code='color',
        type=AttributeType.SELECT,
        is_required=True,
        order=3,
        render_variant=RenderVariant.SWATCHES
    )
    
    AttributeOption.objects.create(
        attribute=color_attr,
        label='Blanco',
        code='blanco',
        pricing_mode=PricingMode.ABS,
        price_value=Decimal('0'),
        swatch_hex='#FFFFFF',
        order=1,
        is_default=True
    )
    
    AttributeOption.objects.create(
        attribute=color_attr,
        label='Negro Mate',
        code='negro-mate',
        pricing_mode=PricingMode.FACTOR,
        price_value=Decimal('1.08'),
        swatch_hex='#000000',
        order=2
    )
    print(f"✅ Atributo creado: {color_attr} con 2 opciones")
    
    # 4. Contramarco (BOOLEAN con PERIMETER)
    contramarco_attr = TemplateAttribute.objects.create(
        template=template,
        name='Contramarco',
        code='contramarco',
        type=AttributeType.BOOLEAN,
        is_required=False,
        order=4,
        rules_json={
            'pricing_mode': 'PERIMETER',
            'price_value': 1500.0000
        }
    )
    print(f"✅ Atributo creado: {contramarco_attr}")
    
    # 5. Vidrio (SELECT con PER_M2)
    vidrio_attr = TemplateAttribute.objects.create(
        template=template,
        name='Vidrio',
        code='vidrio',
        type=AttributeType.SELECT,
        is_required=True,
        order=5
    )
    
    AttributeOption.objects.create(
        attribute=vidrio_attr,
        label='Float 4mm',
        code='float-4mm',
        pricing_mode=PricingMode.PER_M2,
        price_value=Decimal('8900'),
        order=1,
        is_default=True
    )
    
    AttributeOption.objects.create(
        attribute=vidrio_attr,
        label='DVH 4+9+4',
        code='dvh-4-9-4',
        pricing_mode=PricingMode.PER_M2,
        price_value=Decimal('15600'),
        order=2
    )
    print(f"✅ Atributo creado: {vidrio_attr} con 2 opciones")
    
    # 6. Cantidad de tornillos (QUANTITY)
    tornillos_qty_attr = TemplateAttribute.objects.create(
        template=template,
        name='Cantidad de Tornillos',
        code='tornillos_qty',
        type=AttributeType.QUANTITY,
        is_required=True,
        order=6,
        min_value=0,
        max_value=100,
        step_value=1,
        unit_label='u.'
    )
    print(f"✅ Atributo creado: {tornillos_qty_attr}")
    
    # 7. Tipo de tornillo (SELECT con PER_UNIT)
    tornillo_attr = TemplateAttribute.objects.create(
        template=template,
        name='Tipo de Tornillo',
        code='tornillo',
        type=AttributeType.SELECT,
        is_required=True,
        order=7
    )
    
    AttributeOption.objects.create(
        attribute=tornillo_attr,
        label='Tornillo T1',
        code='t1',
        pricing_mode=PricingMode.PER_UNIT,
        price_value=Decimal('120'),
        qty_attr_code='tornillos_qty',
        order=1,
        is_default=True
    )
    
    AttributeOption.objects.create(
        attribute=tornillo_attr,
        label='Tornillo T2 Premium',
        code='t2',
        pricing_mode=PricingMode.PER_UNIT,
        price_value=Decimal('180'),
        qty_attr_code='tornillos_qty',
        order=2
    )
    print(f"✅ Atributo creado: {tornillo_attr} con 2 opciones")
    
    print(f"\n🎉 Plantilla Módena configurada exitosamente con {template.attributes.count()} atributos")
    print(f"📋 Código: {template.code}")
    print(f"💰 Precio base: ${template.base_price_net}")
    print(f"🔗 API: /api/v2/templates/{template.id}/")
    print(f"🧮 Preview: /api/v2/templates/{template.id}/preview_pricing/")
    
    return template

if __name__ == '__main__':
    create_modena_template()