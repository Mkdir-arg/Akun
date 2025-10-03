# Revisar apps disponibles
from django.apps import apps
from django.conf import settings

print('=== APPS INSTALADAS ===')
for app in settings.INSTALLED_APPS:
    print(f'- {app}')

print('\n=== MODELOS DISPONIBLES ===')
for model in apps.get_models():
    print(f'{model._meta.app_label}.{model.__name__}: {model.objects.count()} registros')

print('\n=== INTENTANDO IMPORTAR MODELOS ===')
try:
    from apps.catalog.models import ProductTemplate, TemplateAttribute, AttributeOption
    print(f'✓ ProductTemplate: {ProductTemplate.objects.count()}')
    print(f'✓ TemplateAttribute: {TemplateAttribute.objects.count()}')
    print(f'✓ AttributeOption: {AttributeOption.objects.count()}')
except ImportError as e:
    print(f'✗ Error importando catalog: {e}')

try:
    from apps.sales.models import Quote, QuoteItem
    print(f'✓ Quote: {Quote.objects.count()}')
    print(f'✓ QuoteItem: {QuoteItem.objects.count()}')
except ImportError as e:
    print(f'✗ Error importando sales: {e}')

try:
    from apps.crm.models import Cliente
    print(f'✓ Cliente: {Cliente.objects.count()}')
except ImportError as e:
    print(f'✗ Error importando crm: {e}')