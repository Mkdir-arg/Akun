from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.mixins import TimestampMixin


class User(AbstractUser, TimestampMixin):
    """Modelo de usuario personalizado."""
    
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name() or self.username}"