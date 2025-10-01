from django.core.management.base import BaseCommand
from apps.catalog.models import ProductTemplate, TemplateAttribute, AttributeOption, AttributeType, RenderVariant, PricingMode

class Command(BaseCommand):
    help = 'Crea plantilla de Ventana con filtrado dinámico'

    def handle(self, *args, **options):
        # Crear plantilla base
        template, created = ProductTemplate.objects.get_or_create(
            code='ventana-dinamica',
            defaults={
                'product_class': 'VENTANA',
                'line_name': 'Dinámico',
                'base_price_net': 0,
                'requires_dimensions': True,
                'is_active': True,
                'version': 1
            }
        )
        
        if created:
            self.stdout.write("✅ Plantilla 'ventana-dinamica' creada")
        else:
            self.stdout.write("⚠️ Plantilla 'ventana-dinamica' ya existe")
        
        # Limpiar atributos existentes
        template.attributes.all().delete()
        
        # 1. Línea (SELECT con filtrado dinámico)
        linea_attr = TemplateAttribute.objects.create(
            template=template,
            name='Línea',
            code='linea',
            type=AttributeType.SELECT,
            is_required=True,
            order=1,
            render_variant=RenderVariant.SELECT,
            rules_json={
                'dynamic_source': 'api/lineas/',
                'filters_next': ['marco']
            }
        )
        
        # 2. Marco (SELECT filtrado por línea)
        marco_attr = TemplateAttribute.objects.create(
            template=template,
            name='Marco',
            code='marco',
            type=AttributeType.SELECT,
            is_required=True,
            order=2,
            render_variant=RenderVariant.SELECT,
            rules_json={
                'dynamic_source': 'api/marcos/',
                'depends_on': ['linea'],
                'filters_next': ['hoja']
            }
        )
        
        # 3. Hoja (SELECT filtrado por marco)
        hoja_attr = TemplateAttribute.objects.create(
            template=template,
            name='Hoja',
            code='hoja',
            type=AttributeType.SELECT,
            is_required=True,
            order=3,
            render_variant=RenderVariant.SELECT,
            rules_json={
                'dynamic_source': 'api/hojas/',
                'depends_on': ['marco'],
                'filters_next': ['interior']
            }
        )
        
        # 4. Interior (SELECT filtrado por hoja)
        interior_attr = TemplateAttribute.objects.create(
            template=template,
            name='Interior',
            code='interior',
            type=AttributeType.SELECT,
            is_required=True,
            order=4,
            render_variant=RenderVariant.SELECT,
            rules_json={
                'dynamic_source': 'api/interiores/',
                'depends_on': ['hoja'],
                'enables_options': ['contravidrio', 'vidrio_repartido']
            }
        )
        
        # 5. Dimensiones
        dim_attr = TemplateAttribute.objects.create(
            template=template,
            name='Dimensiones',
            code='dimensiones',
            type=AttributeType.DIMENSIONS_MM,
            is_required=True,
            order=5,
            min_width=300,
            max_width=3000,
            min_height=400,
            max_height=2500,
            step_mm=10
        )
        
        # 6. Cantidad
        qty_attr = TemplateAttribute.objects.create(
            template=template,
            name='Cantidad',
            code='cantidad',
            type=AttributeType.QUANTITY,
            is_required=True,
            order=6,
            min_value=1,
            max_value=100,
            step_value=1,
            unit_label='unidades'
        )
        
        # 7. Contravidrio (BOOLEAN condicional)
        contravidrio_attr = TemplateAttribute.objects.create(
            template=template,
            name='Contravidrio',
            code='contravidrio',
            type=AttributeType.BOOLEAN,
            is_required=False,
            order=7,
            rules_json={
                'conditional': True,
                'depends_on': ['interior'],
                'check_availability': 'api/opciones/?interior_id={interior}'
            }
        )
        
        # 8. Mosquitero (BOOLEAN condicional)
        mosquitero_attr = TemplateAttribute.objects.create(
            template=template,
            name='Mosquitero',
            code='mosquitero',
            type=AttributeType.BOOLEAN,
            is_required=False,
            order=8,
            rules_json={
                'conditional': True,
                'depends_on': ['hoja'],
                'check_availability': 'api/opciones/?hoja_id={hoja}'
            }
        )
        
        # 9. Vidrio Repartido (BOOLEAN condicional)
        vidrio_repartido_attr = TemplateAttribute.objects.create(
            template=template,
            name='Vidrio Repartido',
            code='vidrio_repartido',
            type=AttributeType.BOOLEAN,
            is_required=False,
            order=9,
            rules_json={
                'conditional': True,
                'depends_on': ['interior'],
                'check_availability': 'api/opciones/?interior_id={interior}'
            }
        )
        
        self.stdout.write("✅ Atributos creados:")
        for attr in template.attributes.all().order_by('order'):
            self.stdout.write(f"  {attr.order}. {attr.name} ({attr.type})")
        
        self.stdout.write(f"\n🎯 Plantilla creada con ID: {template.id}")
        self.stdout.write("🔗 Usa el frontend para probar el filtrado dinámico")