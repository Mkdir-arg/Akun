from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Role

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea usuario admin'

    def handle(self, *args, **options):
        # Eliminar admin existente
        User.objects.filter(email='admin@akun.com').delete()
        
        # Obtener rol admin
        admin_role, created = Role.objects.get_or_create(
            name='Administrador',
            defaults={
                'description': 'Acceso completo',
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
            }
        )
        
        # Crear usuario admin
        user = User.objects.create_user(
            username='admin',
            email='admin@akun.com',
            password='admin123',
            first_name='Admin',
            last_name='Sistema',
            role=admin_role,
            is_staff=True,
            is_superuser=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Usuario admin creado: {user.email}')
        )