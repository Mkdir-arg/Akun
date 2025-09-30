from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid


class Presupuesto(models.Model):
    """Presupuesto"""
    STATUS_CHOICES = [
        ('DRAFT', 'Borrador'),
        ('SENT', 'Enviado'),
        ('APPROVED', 'Aprobado'),
        ('REJECTED', 'Rechazado'),
        ('EXPIRED', 'Vencido'),
        ('SOLD', 'Cerrado Vendido'),
        ('CONVERTED', 'Convertido a Venta'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
        ('URGENT', 'Urgente'),
    ]
    
    # Identificación
    number = models.CharField(max_length=20, unique=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Relaciones
    customer = models.ForeignKey('crm.Cliente', on_delete=models.PROTECT, related_name='quotes')
    # price_list = models.ForeignKey('catalog.ListaPrecios', on_delete=models.PROTECT, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_quotes')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_quotes')
    
    # Estado y fechas
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    valid_until = models.DateField(null=True, blank=True)
    
    # Información comercial
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Totales
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.number:
            # Generar número correlativo
            last_quote = Presupuesto.objects.order_by('-id').first()
            if last_quote and last_quote.number:
                try:
                    last_number = int(last_quote.number.split('-')[1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            self.number = f"PRES-{new_number:06d}"
        
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Recalcular totales del presupuesto"""
        items = self.items.all()
        self.subtotal = sum(item.subtotal for item in items)
        self.tax_amount = sum(item.tax_amount for item in items)
        self.total = sum(item.total for item in items) - self.discount_amount
        self.save(update_fields=['subtotal', 'tax_amount', 'total'])
    
    def can_convert_to_order(self):
        """Verificar si se puede convertir a pedido"""
        return self.status in ['SENT', 'APPROVED']
    
    def __str__(self):
        return f"{self.number} - {self.customer.name}"


class LineaPresupuesto(models.Model):
    """Línea de presupuesto"""
    quote = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='items')
    # product = models.ForeignKey('catalog.Producto', on_delete=models.PROTECT, null=True, blank=True)
    
    # Especificaciones del producto
    description = models.TextField(blank=True)  # Descripción personalizada
    width_mm = models.PositiveIntegerField(null=True, blank=True)
    height_mm = models.PositiveIntegerField(null=True, blank=True)
    
    # Cantidades y precios
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Totales calculados
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Orden de visualización
    line_number = models.PositiveSmallIntegerField(default=1)
    
    # Para servicios
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_quote_items')
    
    class Meta:
        verbose_name = 'Línea de Presupuesto'
        verbose_name_plural = 'Líneas de Presupuesto'
        ordering = ['line_number']
        unique_together = ('quote', 'line_number')
    
    def save(self, *args, **kwargs):
        # El unit_price incluye IVA, calcular subtotal sin IVA
        total_with_tax = self.quantity * self.unit_price
        self.discount_amount = total_with_tax * (self.discount_pct / 100)
        total_after_discount = total_with_tax - self.discount_amount
        
        # Calcular subtotal (sin IVA) y tax_amount
        tax_factor = 1 + (self.tax_rate / 100)
        self.subtotal = total_after_discount / tax_factor
        self.tax_amount = total_after_discount - self.subtotal
        self.total = total_after_discount
        
        super().save(*args, **kwargs)
        
        # Recalcular totales del presupuesto
        self.quote.calculate_totals()
    
    def delete(self, *args, **kwargs):
        quote = self.quote
        super().delete(*args, **kwargs)
        quote.calculate_totals()
    
    def __str__(self):
        return f"{self.quote.number} - Línea {self.line_number}"


class Pedido(models.Model):
    """Pedido/Venta"""
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmado'),
        ('IN_PRODUCTION', 'En Producción'),
        ('READY', 'Listo'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PARTIAL', 'Parcial'),
        ('PAID', 'Pagado'),
        ('OVERDUE', 'Vencido'),
    ]
    
    TYPE_CHOICES = [
        ('DIRECT', 'Venta Directa'),
        ('FROM_QUOTE', 'Desde Presupuesto'),
    ]
    
    # Identificación
    number = models.CharField(max_length=20, unique=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Relaciones
    customer = models.ForeignKey('crm.Cliente', on_delete=models.PROTECT, related_name='orders')
    quote = models.ForeignKey(Presupuesto, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    # price_list = models.ForeignKey('catalog.ListaPrecios', on_delete=models.PROTECT, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_orders')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
    
    # Tipo y estado
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='DIRECT')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    
    # Fechas importantes
    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Información comercial
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Totales
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['order_date']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.number:
            # Generar número correlativo
            last_order = Pedido.objects.order_by('-id').first()
            if last_order and last_order.number:
                try:
                    last_number = int(last_order.number.split('-')[1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            self.number = f"PED-{new_number:06d}"
        
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Recalcular totales del pedido"""
        items = self.items.all()
        self.subtotal = sum(item.subtotal for item in items)
        self.tax_amount = sum(item.tax_amount for item in items)
        self.total = sum(item.total for item in items) - self.discount_amount
        self.save(update_fields=['subtotal', 'tax_amount', 'total'])
    
    @classmethod
    def create_from_quote(cls, quote, created_by):
        """Crear pedido desde presupuesto"""
        if not quote.can_convert_to_order():
            raise ValidationError('El presupuesto no puede ser convertido a pedido')
        
        # Crear el pedido
        order = cls.objects.create(
            customer=quote.customer,
            quote=quote,
            # price_list=quote.price_list,
            created_by=created_by,
            type='FROM_QUOTE',
            title=f'Pedido desde {quote.number}',
            description=quote.description,
            notes=quote.notes,
        )
        
        # Copiar líneas del presupuesto
        for quote_item in quote.items.all():
            LineaPedido.objects.create(
                order=order,
                # product=quote_item.product,
                description=quote_item.description,
                width_mm=quote_item.width_mm,
                height_mm=quote_item.height_mm,
                quantity=quote_item.quantity,
                unit_price=quote_item.unit_price,
                discount_pct=quote_item.discount_pct,
                tax_rate=quote_item.tax_rate,
                line_number=quote_item.line_number,
            )
        
        # Marcar presupuesto como vendido
        quote.status = 'SOLD'
        quote.save()
        
        return order
    
    def __str__(self):
        return f"{self.number} - {self.customer.name}"


class LineaPedido(models.Model):
    """Línea de pedido"""
    order = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    # product = models.ForeignKey('catalog.Producto', on_delete=models.PROTECT)
    
    # Especificaciones del producto
    description = models.TextField(blank=True)
    width_mm = models.PositiveIntegerField(null=True, blank=True)
    height_mm = models.PositiveIntegerField(null=True, blank=True)
    
    # Cantidades y precios
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Totales calculados
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Control de producción
    line_number = models.PositiveSmallIntegerField(default=1)
    production_status = models.CharField(max_length=15, choices=[
        ('PENDING', 'Pendiente'),
        ('IN_PROGRESS', 'En Proceso'),
        ('COMPLETED', 'Completado'),
    ], default='PENDING')
    
    class Meta:
        verbose_name = 'Línea de Pedido'
        verbose_name_plural = 'Líneas de Pedido'
        ordering = ['line_number']
        unique_together = ('order', 'line_number')
    
    def save(self, *args, **kwargs):
        # El unit_price incluye IVA, calcular subtotal sin IVA
        total_with_tax = self.quantity * self.unit_price
        self.discount_amount = total_with_tax * (self.discount_pct / 100)
        total_after_discount = total_with_tax - self.discount_amount
        
        # Calcular subtotal (sin IVA) y tax_amount
        tax_factor = 1 + (self.tax_rate / 100)
        self.subtotal = total_after_discount / tax_factor
        self.tax_amount = total_after_discount - self.subtotal
        self.total = total_after_discount
        
        super().save(*args, **kwargs)
        
        # Recalcular totales del pedido
        self.order.calculate_totals()
    
    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        order.calculate_totals()
    
    def __str__(self):
        return f"{self.order.number} - Línea {self.line_number}"