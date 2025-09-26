from django.db import models, transaction
from django.core.exceptions import ValidationError
from decimal import Decimal


class Customer(models.Model):
    TYPE_CHOICES = [
        ('PERSONA', 'Persona'),
        ('EMPRESA', 'Empresa'),
    ]
    
    code = models.CharField(max_length=20, unique=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    name = models.CharField(max_length=200, db_index=True)
    tax_id = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    default_price_list = models.ForeignKey(
        'catalog.PriceList', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        indexes = [
            models.Index(fields=['name']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tax_id'],
                condition=~models.Q(tax_id=''),
                name='unique_tax_id_when_not_empty'
            )
        ]
        
    def save(self, *args, **kwargs):
        if not self.code:
            with transaction.atomic():
                # Generar código correlativo
                last_customer = Customer.objects.select_for_update().order_by('-id').first()
                if last_customer and last_customer.code:
                    try:
                        last_number = int(last_customer.code[1:])  # Quitar 'C' del inicio
                        new_number = last_number + 1
                    except (ValueError, IndexError):
                        new_number = 1
                else:
                    new_number = 1
                self.code = f"C{new_number:05d}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.code} - {self.name}"


class Address(models.Model):
    KIND_CHOICES = [
        ('FACTURACION', 'Facturación'),
        ('ENVIO', 'Envío'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    kind = models.CharField(max_length=15, choices=KIND_CHOICES)
    street = models.CharField(max_length=200)
    number = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Argentina')
    is_default = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'kind'],
                condition=models.Q(is_default=True),
                name='unique_default_address_per_customer_kind'
            )
        ]
        
    def clean(self):
        if self.is_default:
            # Verificar que no haya otra dirección default del mismo tipo para el mismo cliente
            existing = Address.objects.filter(
                customer=self.customer,
                kind=self.kind,
                is_default=True
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError(
                    f'Ya existe una dirección por defecto de tipo {self.get_kind_display()} para este cliente.'
                )
                
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.street} {self.number}, {self.city} ({self.get_kind_display()})"