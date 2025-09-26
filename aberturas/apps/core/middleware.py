import logging
import time
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.http import JsonResponse
import json

logger = logging.getLogger('transactions')


class SecurityMiddleware(MiddlewareMixin):
    """Middleware de seguridad para protección contra ataques"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        # Rate limiting por IP
        if self.is_rate_limited(request):
            return JsonResponse({'error': 'Demasiadas solicitudes'}, status=429)
        
        # Bloquear IPs sospechosas
        if self.is_blocked_ip(request):
            return HttpResponseForbidden('IP bloqueada')
        
        # Validar User-Agent
        if not self.is_valid_user_agent(request):
            return HttpResponseForbidden('User-Agent inválido')
        
        return None
    
    def is_rate_limited(self, request):
        """Rate limiting: máximo 100 requests por minuto por IP"""
        ip = self.get_client_ip(request)
        cache_key = f'rate_limit_{ip}'
        
        current_requests = cache.get(cache_key, 0)
        if current_requests >= 100:
            return True
        
        cache.set(cache_key, current_requests + 1, 60)  # 60 segundos
        return False
    
    def is_blocked_ip(self, request):
        """Verificar si la IP está en lista negra"""
        ip = self.get_client_ip(request)
        blocked_ips = cache.get('blocked_ips', set())
        return ip in blocked_ips
    
    def is_valid_user_agent(self, request):
        """Validar User-Agent para bloquear bots maliciosos"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Bloquear User-Agents sospechosos
        suspicious_agents = [
            'sqlmap', 'nikto', 'nmap', 'masscan', 'zap',
            'burp', 'w3af', 'acunetix', 'nessus'
        ]
        
        return not any(agent in user_agent for agent in suspicious_agents)
    
    def get_client_ip(self, request):
        """Obtener IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LoginAttemptMiddleware(MiddlewareMixin):
    """Middleware para controlar intentos de login"""
    
    def process_request(self, request):
        if request.path in ['/api/login/', '/api/auth/'] and request.method == 'POST':
            ip = self.get_client_ip(request)
            
            # Verificar intentos fallidos
            failed_attempts = cache.get(f'failed_login_{ip}', 0)
            if failed_attempts >= 5:
                # Bloquear por 15 minutos después de 5 intentos fallidos
                return JsonResponse({
                    'error': 'Demasiados intentos fallidos. Intente en 15 minutos.'
                }, status=429)
        
        return None
    
    def process_response(self, request, response):
        if request.path in ['/api/login/', '/api/auth/'] and request.method == 'POST':
            ip = self.get_client_ip(request)
            
            if response.status_code == 400:  # Login fallido
                failed_attempts = cache.get(f'failed_login_{ip}', 0)
                cache.set(f'failed_login_{ip}', failed_attempts + 1, 900)  # 15 minutos
            elif response.status_code == 200:  # Login exitoso
                cache.delete(f'failed_login_{ip}')
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SessionSecurityMiddleware(MiddlewareMixin):
    """Middleware para seguridad de sesiones"""
    
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Verificar timeout de sesión (30 minutos de inactividad)
            last_activity = request.session.get('last_activity')
            if last_activity:
                if time.time() - last_activity > 1800:  # 30 minutos
                    logout(request)
                    return JsonResponse({'error': 'Sesión expirada'}, status=401)
            
            # Actualizar última actividad
            request.session['last_activity'] = time.time()
            
            # Verificar IP de sesión (opcional)
            session_ip = request.session.get('session_ip')
            current_ip = self.get_client_ip(request)
            
            if session_ip and session_ip != current_ip:
                logout(request)
                return JsonResponse({'error': 'IP de sesión inválida'}, status=401)
            
            if not session_ip:
                request.session['session_ip'] = current_ip
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class TransactionLoggerMiddleware(MiddlewareMixin):
    """Middleware para logging de transacciones críticas"""
    
    def process_response(self, request, response):
        # Log de operaciones críticas
        if request.method in ['POST', 'PUT', 'DELETE'] and hasattr(request, 'user') and request.user.is_authenticated:
            if any(path in request.path for path in ['/api/users/', '/api/roles/', '/api/customers/', '/api/products/']):
                logger.info(
                    f"🔒 {request.method} {request.path} | "
                    f"Usuario: {request.user.username} | "
                    f"IP: {self.get_client_ip(request)} | "
                    f"Status: {response.status_code}"
                )
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip