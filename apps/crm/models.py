from django.db import models, transaction

class Cliente(models.Model):
    TYPE_CHOICES = [
        ('PERSONA', 'Persona'),
        ('EMPRESA', 'Empresa'),
    ]
    
    code = models.CharField(max_length=16, unique=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='EMPRESA')
    name = models.CharField(max_length=255, db_index=True)
    tax_id = models.CharField(max_length=20, null=True, blank=True, unique=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=40, null=True, blank=True)
    
    # Dirección básica
    address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    def save(self, *args, **kwargs):
        if not self.code:
            with transaction.atomic():
                last_customer = Cliente.objects.select_for_update().order_by('-id').first()
                if last_customer and last_customer.code:
                    try:
                        last_number = int(last_customer.code[1:])
                        new_number = last_number + 1
                    except (ValueError, IndexError):
                        new_number = 1
                else:
                    new_number = 1
                self.code = f"C{new_number:05d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.code} - {self.name}"