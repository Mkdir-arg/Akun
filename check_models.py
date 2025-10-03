# Importar todos los modelos
from django.apps import apps
from catalog.models import *
from sales.models import *
from crm.models import *

# Mostrar todos los modelos disponibles
print('=== MODELOS DISPONIBLES ===')
for model in apps.get_models():
    print(f'{model._meta.app_label}.{model.__name__}: {model.objects.count()} registros')

print('\n=== ANÁLISIS DE PLANTILLAS ===')
print(f'Total ProductTemplate: {ProductTemplate.objects.count()}')
if ProductTemplate.objects.exists():
    print('Primeras 5 plantillas:')
    for p in ProductTemplate.objects.all()[:5]:
        print(f'  - {p.id}: {p.name} (Línea: {p.linea}, Marco: {p.marco})')

print('\n=== ANÁLISIS DE ATRIBUTOS ===')
print(f'Total TemplateAttribute: {TemplateAttribute.objects.count()}')
if TemplateAttribute.objects.exists():
    print('Tipos de atributos:')
    for attr in TemplateAttribute.objects.values('attribute_type').distinct():
        count = TemplateAttribute.objects.filter(attribute_type=attr['attribute_type']).count()
        print(f'  - {attr["attribute_type"]}: {count} atributos')

print('\n=== ANÁLISIS DE OPCIONES ===')
print(f'Total AttributeOption: {AttributeOption.objects.count()}')
if AttributeOption.objects.exists():
    print('Opciones por atributo (primeros 10):')
    for opt in AttributeOption.objects.select_related('attribute')[:10]:
        print(f'  - {opt.attribute.name}: {opt.value} (${opt.price_modifier})')

print('\n=== ANÁLISIS DE RELACIONES ===')
if ProductTemplate.objects.exists():
    template = ProductTemplate.objects.first()
    print(f'Plantilla ejemplo: {template.name}')
    print(f'  - Atributos: {template.attributes.count()}')
    for attr in template.attributes.all()[:3]:
        print(f'    * {attr.name}: {attr.options.count()} opciones')