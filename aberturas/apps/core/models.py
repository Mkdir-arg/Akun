from django.db import models
from decimal import Decimal


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True, help_text="Código ISO de la moneda (USD, ARS, etc.)")
    name = models.CharField(max_length=100, help_text="Nombre completo de la moneda")
    symbol = models.CharField(max_length=5, help_text="Símbolo de la moneda ($, €, etc.)")
    exchange_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('1.00'),
        help_text="Tipo de cambio respecto a la moneda base"
    )
    is_default = models.BooleanField(default=False, help_text="Moneda por defecto del sistema")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Moneda"
        verbose_name_plural = "Monedas"
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        # Si esta moneda se marca como default, desmarcar las demás
        if self.is_default:
            Currency.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)