from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.conf import settings
from decimal import Decimal


class Customer(models.Model):
    TYPE_CHOICES = [
        ('PERSONA', 'Persona'),
        ('EMPRESA', 'Empresa'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('POTENCIAL', 'Potencial'),
    ]
    
    code = models.CharField(max_length=16, unique=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='EMPRESA')
    name = models.CharField(max_length=255, db_index=True)
    tax_id = models.CharField(max_length=20, null=True, blank=True, unique=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=40, null=True, blank=True)
    default_price_list = models.ForeignKey(
        'catalog.PriceList', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    payment_terms = models.ForeignKey(
        'PaymentTerm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVO')
    tags = models.ManyToManyField('CustomerTag', blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        indexes = [
            models.Index(fields=['name'], name='crm_customer_name_idx'),
            models.Index(fields=['status'], name='crm_customer_status_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tax_id'],
                condition=~models.Q(tax_id=None),
                name='uniq_customer_tax_id'
            )
        ]
        
    def clean(self):
        # Normalizar tax_id
        if self.tax_id:
            self.tax_id = self.tax_id.strip().upper()
        if self.tax_id == '':
            self.tax_id = None
            
        # Validar nombre para personas
        if self.type == 'PERSONA' and len(self.name.strip()) < 3:
            raise ValidationError('El nombre de una persona debe tener al menos 3 caracteres.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        
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
                
        # Sincronizar status con is_active
        if self.status == 'INACTIVO':
            self.is_active = False
        elif self.status == 'ACTIVO':
            self.is_active = True
            
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
                name='uniq_default_address_per_kind'
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


class Contact(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    role = models.CharField(max_length=80, blank=True)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'
        constraints = [
            models.UniqueConstraint(
                fields=['customer'],
                condition=models.Q(is_primary=True),
                name='uniq_primary_contact_per_customer'
            )
        ]
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def clean(self):
        if self.is_primary:
            existing = Contact.objects.filter(
                customer=self.customer,
                is_primary=True
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError('Ya existe un contacto principal para este cliente.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} ({self.customer.name})"


class PaymentTerm(models.Model):
    name = models.CharField(max_length=100, unique=True)
    days = models.PositiveSmallIntegerField()
    early_discount_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Término de Pago'
        verbose_name_plural = 'Términos de Pago'
        ordering = ['days']
    
    def __str__(self):
        return self.name


class CustomerTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, blank=True, help_text='Color hex (ej: #FF5733)')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Etiqueta de Cliente'
        verbose_name_plural = 'Etiquetas de Cliente'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CustomerNote(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Nota de Cliente'
        verbose_name_plural = 'Notas de Cliente'
        ordering = ['-pinned', '-created_at']
    
    def __str__(self):
        return f"Nota de {self.customer.name} - {self.created_at.strftime('%d/%m/%Y')}"


class CustomerFile(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='customers/files/%Y/%m/')
    title = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Archivo de Cliente'
        verbose_name_plural = 'Archivos de Cliente'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title or self.file.name} - {self.customer.name}"