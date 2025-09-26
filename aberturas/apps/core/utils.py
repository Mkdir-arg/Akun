import hashlib
import secrets
import logging
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()
logger = logging.getLogger('transactions')


def generate_secure_token():
    """Genera un token seguro"""
    return secrets.token_urlsafe(32)


def hash_sensitive_data(data):
    """Hash de datos sensibles para logs"""
    return hashlib.sha256(str(data).encode()).hexdigest()[:8]


def log_security_event(event_type, user, ip_address, details=None):
    """Log de eventos de seguridad"""
    logger.warning(
        f"🚨 SECURITY: {event_type} | "
        f"Usuario: {user.username if user else 'Anónimo'} | "
        f"IP: {ip_address} | "
        f"Detalles: {details or 'N/A'}"
    )


def check_suspicious_activity(user, ip_address):
    """Verificar actividad sospechosa"""
    cache_key = f'activity_{user.id}_{ip_address}'
    activity = cache.get(cache_key, [])
    
    # Agregar timestamp actual
    now = timezone.now()
    activity.append(now.timestamp())
    
    # Mantener solo últimos 10 minutos
    ten_minutes_ago = (now - timedelta(minutes=10)).timestamp()
    activity = [ts for ts in activity if ts > ten_minutes_ago]
    
    # Si más de 50 requests en 10 minutos, es sospechoso
    if len(activity) > 50:
        log_security_event(
            'SUSPICIOUS_ACTIVITY',
            user,
            ip_address,
            f'{len(activity)} requests en 10 minutos'
        )
        return True
    
    cache.set(cache_key, activity, 600)  # 10 minutos
    return False


def sanitize_input(data):
    """Sanitizar entrada de usuario"""
    if isinstance(data, str):
        # Remover caracteres peligrosos
        dangerous_chars = ['<', '>', '"', "'", '&', 'script', 'javascript:', 'onload=']
        for char in dangerous_chars:
            data = data.replace(char, '')
    
    return data


def validate_file_upload(file):
    """Validar archivos subidos"""
    # Tamaño máximo: 10MB
    if file.size > 10 * 1024 * 1024:
        raise ValueError('Archivo demasiado grande (máximo 10MB)')
    
    # Tipos MIME permitidos
    allowed_types = [
        'image/jpeg', 'image/png', 'image/gif',
        'application/pdf', 'text/plain',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]
    
    if file.content_type not in allowed_types:
        raise ValueError(f'Tipo de archivo no permitido: {file.content_type}')
    
    return True


def get_client_ip(request):
    """Obtener IP real del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_safe_redirect_url(url):
    """Verificar si URL de redirección es segura"""
    if not url:
        return False
    
    # Solo permitir URLs relativas o del mismo dominio
    if url.startswith('/') and not url.startswith('//'):
        return True
    
    # Verificar dominio permitido
    allowed_domains = ['localhost', '127.0.0.1', 'tu-dominio.com']
    for domain in allowed_domains:
        if url.startswith(f'http://{domain}') or url.startswith(f'https://{domain}'):
            return True
    
    return False