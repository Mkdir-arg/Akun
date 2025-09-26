from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Asigna permisos por grupos para el dominio CRM y Catalog'

    def handle(self, *args, **options):
        # Crear grupos si no existen
        admin_group, _ = Group.objects.get_or_create(name='Administración')
        sales_group, _ = Group.objects.get_or_create(name='Ventas')
        warehouse_group, _ = Group.objects.get_or_create(name='Depósito')
        production_group, _ = Group.objects.get_or_create(name='Producción')

        # Obtener content types
        crm_models = ['customer', 'address']
        catalog_models = ['uom', 'productcategory', 'taxrate', 'product', 'pricelist', 'pricelistrule']

        # Administración: todos los permisos
        admin_perms = []
        for app_label in ['crm', 'catalog']:
            models = crm_models if app_label == 'crm' else catalog_models
            for model in models:
                try:
                    ct = ContentType.objects.get(app_label=f'apps.{app_label}', model=model)
                    perms = Permission.objects.filter(content_type=ct)
                    admin_perms.extend(perms)
                except ContentType.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'ContentType no encontrado: {app_label}.{model}')
                    )

        admin_group.permissions.set(admin_perms)
        self.stdout.write(
            self.style.SUCCESS(f'Asignados {len(admin_perms)} permisos al grupo Administración')
        )

        # Ventas: add/change/view Customer, Address, PriceList, PriceListRule; view otros
        sales_perms = []
        
        # Permisos completos para Customer, Address, PriceList, PriceListRule
        full_access_models = [
            ('crm', 'customer'),
            ('crm', 'address'),
            ('catalog', 'pricelist'),
            ('catalog', 'pricelistrule')
        ]
        
        for app_label, model in full_access_models:
            try:
                ct = ContentType.objects.get(app_label=f'apps.{app_label}', model=model)
                perms = Permission.objects.filter(
                    content_type=ct,
                    codename__in=[f'add_{model}', f'change_{model}', f'view_{model}']
                )
                sales_perms.extend(perms)
            except ContentType.DoesNotExist:
                pass

        # Solo view para otros modelos del catálogo
        view_only_models = [
            ('catalog', 'product'),
            ('catalog', 'productcategory'),
            ('catalog', 'uom'),
            ('catalog', 'taxrate')
        ]
        
        for app_label, model in view_only_models:
            try:
                ct = ContentType.objects.get(app_label=f'apps.{app_label}', model=model)
                perm = Permission.objects.get(content_type=ct, codename=f'view_{model}')
                sales_perms.append(perm)
            except (ContentType.DoesNotExist, Permission.DoesNotExist):
                pass

        sales_group.permissions.set(sales_perms)
        self.stdout.write(
            self.style.SUCCESS(f'Asignados {len(sales_perms)} permisos al grupo Ventas')
        )

        # Depósito: solo view de catálogo
        warehouse_perms = []
        for model in catalog_models:
            try:
                ct = ContentType.objects.get(app_label='apps.catalog', model=model)
                perm = Permission.objects.get(content_type=ct, codename=f'view_{model}')
                warehouse_perms.append(perm)
            except (ContentType.DoesNotExist, Permission.DoesNotExist):
                pass

        warehouse_group.permissions.set(warehouse_perms)
        self.stdout.write(
            self.style.SUCCESS(f'Asignados {len(warehouse_perms)} permisos al grupo Depósito')
        )

        # Producción: view Product y ProductCategory
        production_perms = []
        for model in ['product', 'productcategory']:
            try:
                ct = ContentType.objects.get(app_label='apps.catalog', model=model)
                perm = Permission.objects.get(content_type=ct, codename=f'view_{model}')
                production_perms.append(perm)
            except (ContentType.DoesNotExist, Permission.DoesNotExist):
                pass

        production_group.permissions.set(production_perms)
        self.stdout.write(
            self.style.SUCCESS(f'Asignados {len(production_perms)} permisos al grupo Producción')
        )

        self.stdout.write(self.style.SUCCESS('Permisos asignados correctamente'))