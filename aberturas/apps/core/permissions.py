from rest_framework.permissions import BasePermission
from django.core.cache import cache


class RoleBasedPermission(BasePermission):
    """Permiso basado en roles del usuario"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superusuarios tienen acceso completo
        if request.user.is_superuser:
            return True
        
        # Verificar si el usuario tiene rol
        if not request.user.role:
            return False
        
        # Mapear vistas a módulos
        module_map = {
            'customer': 'crm',
            'address': 'crm',
            'contact': 'crm',
            'product': 'catalog',
            'category': 'catalog',
            'uom': 'catalog',
            'role': 'settings',
            'user': 'settings',
        }
        
        # Obtener módulo de la vista
        view_name = getattr(view, 'basename', '').lower()
        module = module_map.get(view_name)
        
        if not module:
            return True  # Permitir si no está mapeado
        
        # Verificar acceso al módulo
        return request.user.has_module_access(module)
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        if not request.user.role:
            return False
        
        # Verificar permisos de acción
        if request.method in ['POST'] and not request.user.role.can_create:
            return False
        elif request.method in ['PUT', 'PATCH'] and not request.user.role.can_edit:
            return False
        elif request.method in ['DELETE'] and not request.user.role.can_delete:
            return False
        
        return True


class IPWhitelistPermission(BasePermission):
    """Permiso basado en whitelist de IPs"""
    
    def has_permission(self, request, view):
        # Lista de IPs permitidas (configurar según necesidad)
        allowed_ips = cache.get('allowed_ips', set())
        
        if not allowed_ips:
            return True  # Si no hay whitelist, permitir
        
        client_ip = self.get_client_ip(request)
        return client_ip in allowed_ips
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AdminOnlyPermission(BasePermission):
    """Permiso solo para administradores"""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_superuser or 
             (request.user.role and request.user.role.can_access_settings))
        )