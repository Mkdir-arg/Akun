"""
Mixins reutilizables para vistas y modelos.
"""

from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    """Mixin para agregar timestamps a los modelos."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')

    class Meta:
        abstract = True


# AuthRequiredMixin se define en las vistas donde se necesite
# para evitar problemas de importación circular