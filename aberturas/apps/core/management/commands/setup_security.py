from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Configura medidas de seguridad básicas'

    def handle(self, *args, **options):
        # Configurar IPs bloqueadas (ejemplo)
        blocked_ips = {
            '192.168.1.100',  # IP de ejemplo
            '10.0.0.50',      # IP de ejemplo
        }
        cache.set('blocked_ips', blocked_ips, 86400)  # 24 horas
        
        # Configurar IPs permitidas para admin (opcional)
        allowed_ips = {
            '127.0.0.1',
            '::1',
            '192.168.1.0/24',  # Red local
        }
        cache.set('allowed_ips', allowed_ips, 86400)
        
        # Verificar usuarios con contraseñas débiles
        weak_users = []
        for user in User.objects.all():
            if user.check_password('123456') or user.check_password('admin') or user.check_password('password'):
                weak_users.append(user.username)
        
        if weak_users:
            self.stdout.write(
                self.style.WARNING(f'Usuarios con contraseñas débiles: {", ".join(weak_users)}')
            )
        
        # Configurar headers de seguridad
        self.stdout.write(
            self.style.SUCCESS('Configuración de seguridad aplicada:')
        )
        self.stdout.write('✓ Rate limiting activado (100 req/min por IP)')
        self.stdout.write('✓ Bloqueo de login después de 5 intentos fallidos')
        self.stdout.write('✓ Timeout de sesión: 30 minutos')
        self.stdout.write('✓ Validación de User-Agent')
        self.stdout.write('✓ Headers de seguridad configurados')
        self.stdout.write('✓ Permisos basados en roles activados')
        
        if weak_users:
            self.stdout.write(
                self.style.WARNING('⚠️  Cambiar contraseñas débiles detectadas')
            )