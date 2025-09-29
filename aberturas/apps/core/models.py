from django.db import models
from decimal import Decimal


class Moneda(models.Model):
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
            Moneda.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Provincia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Provincia"
        verbose_name_plural = "Provincias"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Municipio(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name='municipios')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Municipio"
        verbose_name_plural = "Municipios"
        ordering = ['nombre']
        unique_together = ['nombre', 'provincia']

    def __str__(self):
        return f"{self.nombre}, {self.provincia.nombre}"


class Localidad(models.Model):
    nombre = models.CharField(max_length=100)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE, related_name='localidades')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"
        ordering = ['nombre']
        unique_together = ['nombre', 'municipio']

    def __str__(self):
        return f"{self.nombre}, {self.municipio.nombre}"