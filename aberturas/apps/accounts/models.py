from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    # Permisos por módulo
    can_access_crm = models.BooleanField(default=False, verbose_name='Acceso a CRM')
    can_access_catalog = models.BooleanField(default=False, verbose_name='Acceso a Catálogo')
    can_access_orders = models.BooleanField(default=False, verbose_name='Acceso a Pedidos')
    can_access_quotes = models.BooleanField(default=False, verbose_name='Acceso a Presupuestos')
    can_access_reports = models.BooleanField(default=False, verbose_name='Acceso a Reportes')
    can_access_settings = models.BooleanField(default=False, verbose_name='Acceso a Configuración')
    
    # Permisos específicos
    can_create = models.BooleanField(default=True, verbose_name='Puede crear')
    can_edit = models.BooleanField(default=True, verbose_name='Puede editar')
    can_delete = models.BooleanField(default=False, verbose_name='Puede eliminar')
    can_export = models.BooleanField(default=False, verbose_name='Puede exportar')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def has_module_access(self, module):
        if self.is_superuser:
            return True
        if not self.role:
            return False
        
        module_permissions = {
            'crm': self.role.can_access_crm,
            'catalog': self.role.can_access_catalog,
            'orders': self.role.can_access_orders,
            'quotes': self.role.can_access_quotes,
            'reports': self.role.can_access_reports,
            'settings': self.role.can_access_settings,
        }
        
        return module_permissions.get(module, False)