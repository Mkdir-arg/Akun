from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Role

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea roles y usuarios de prueba'

    def handle(self, *args, **options):
        # Crear roles
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
                'name': 'Vendedor',
                'description': 'Acceso a CRM, catálogo y presupuestos',
                'can_access_crm': True,
                'can_access_catalog': True,
                'can_access_orders': False,
                'can_access_quotes': True,
                'can_access_reports': False,
                'can_access_settings': False,
                'can_create': True,
                'can_edit': True,
                'can_delete': False,
                'can_export': False,
            },
            {
                'name': 'Operador',
                'description': 'Acceso a pedidos y catálogo',
                'can_access_crm': False,
                'can_access_catalog': True,
                'can_access_orders': True,
                'can_access_quotes': False,
                'can_access_reports': False,
                'can_access_settings': False,
                'can_create': True,
                'can_edit': True,
                'can_delete': False,
                'can_export': False,
            },
            {
                'name': 'Consulta',
                'description': 'Solo lectura en todos los módulos',
                'can_access_crm': True,
                'can_access_catalog': True,
                'can_access_orders': True,
                'can_access_quotes': True,
                'can_access_reports': True,
                'can_access_settings': False,
                'can_create': False,
                'can_edit': False,
                'can_delete': False,
                'can_export': True,
            },
        ]

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            if created:
                self.stdout.write(f'Rol creado: {role}')

        # Crear usuarios de prueba
        admin_role = Role.objects.get(name='Administrador')
        vendedor_role = Role.objects.get(name='Vendedor')
        
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@akun.com',
                'first_name': 'Admin',
                'last_name': 'Sistema',
                'password': 'admin123',
                'role': admin_role,
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'vendedor1',
                'email': 'vendedor@akun.com',
                'first_name': 'Juan',
                'last_name': 'Vendedor',
                'password': 'vendedor123',
                'role': vendedor_role,
                'is_staff': False,
                'is_superuser': False,
            },
        ]

        for user_data in users_data:
            if not User.objects.filter(email=user_data['email']).exists():
                password = user_data.pop('password')
                user = User.objects.create_user(**user_data)
                user.set_password(password)
                user.save()
                self.stdout.write(f'Usuario creado: {user}')

        self.stdout.write(
            self.style.SUCCESS('Roles y usuarios creados exitosamente')
        )