from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from apps.core.constants import USER_GROUPS


class Command(BaseCommand):
    help = 'Crear grupos de usuarios por defecto'

    def handle(self, *args, **options):
        for group_key, group_name in USER_GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Grupo "{group_name}" creado exitosamente')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Grupo "{group_name}" ya existe')
                )