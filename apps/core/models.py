from django.db import models

class Moneda(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Moneda'
        verbose_name_plural = 'Monedas'
    
    def __str__(self):
        return f"{self.name} ({self.code})"