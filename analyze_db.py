# Análisis completo de la base de datos
from apps.catalog.models import ProductTemplate, TemplateAttribute, AttributeOption

print('=== ANÁLISIS COMPLETO DE LA BASE DE DATOS ===')

# Plantillas
print(f'\n📋 PLANTILLAS: {ProductTemplate.objects.count()} registros')
if ProductTemplate.objects.exists():
    print('\nPrimeras plantillas:')
    for p in ProductTemplate.objects.all()[:10]:
        print(f'  - ID:{p.id} | {p.name} | Línea:{p.linea} | Marco:{p.marco} | Hoja:{p.hoja} | Interior:{p.interior}')
    
    print('\n📊 DISTRIBUCIÓN POR LÍNEA:')
    from django.db.models import Count
    lineas = ProductTemplate.objects.values('linea').annotate(count=Count('id')).order_by('-count')
    for linea in lineas:
        print(f'  - {linea["linea"]}: {linea["count"]} plantillas')
    
    print('\n📊 DISTRIBUCIÓN POR MARCO:')
    marcos = ProductTemplate.objects.values('marco').annotate(count=Count('id')).order_by('-count')[:10]
    for marco in marcos:
        print(f'  - {marco["marco"]}: {marco["count"]} plantillas')

# Atributos
print(f'\n🏷️ ATRIBUTOS: {TemplateAttribute.objects.count()} registros')
if TemplateAttribute.objects.exists():
    print('\nAtributos disponibles:')
    for attr in TemplateAttribute.objects.all():
        print(f'  - {attr.name} ({attr.attribute_type}) - Opciones: {attr.options.count()}')

# Opciones
print(f'\n⚙️ OPCIONES: {AttributeOption.objects.count()} registros')
if AttributeOption.objects.exists():
    print('\nPrimeras opciones:')
    for opt in AttributeOption.objects.select_related('attribute')[:10]:
        print(f'  - {opt.attribute.name}: {opt.value} (${opt.price_modifier})')

# Relaciones
print('\n🔗 ANÁLISIS DE RELACIONES:')
if ProductTemplate.objects.exists():
    template = ProductTemplate.objects.first()
    print(f'\nPlantilla ejemplo: {template.name}')
    print(f'  - Atributos relacionados: {template.attributes.count()}')
    for attr in template.attributes.all():
        print(f'    * {attr.name}: {attr.options.count()} opciones')
        for opt in attr.options.all()[:3]:
            print(f'      - {opt.value} (${opt.price_modifier})')

print('\n=== RESUMEN FINAL ===')
print(f'Total plantillas: {ProductTemplate.objects.count()}')
print(f'Total atributos: {TemplateAttribute.objects.count()}')
print(f'Total opciones: {AttributeOption.objects.count()}')