from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from decimal import Decimal


class UoM(models.Model):
    CATEGORY_CHOICES = [
        ('length', 'Longitud'),
        ('area', 'Área'),
        ('weight', 'Peso'),
        ('unit', 'Unidad'),
    ]
    
    code = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        
    def __str__(self):
        return f"{self.name} ({self.code})"


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    code = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Producto'
        unique_together = ('parent', 'name')
        
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class TaxRate(models.Model):
    name = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Tasa de Impuesto'
        verbose_name_plural = 'Tasas de Impuesto'
        
    def clean(self):
        if self.is_default and TaxRate.objects.filter(is_default=True).exclude(pk=self.pk).exists():
            raise ValidationError('Solo puede haber una tasa de impuesto por defecto.')
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name


class Product(models.Model):
    MATERIAL_CHOICES = [
        ('ALUMINIO', 'Aluminio'),
        ('PVC', 'PVC'),
        ('MADERA', 'Madera'),
    ]
    
    OPENING_TYPE_CHOICES = [
        ('CORREDIZA', 'Corrediza'),
        ('BATIENTE', 'Batiente'),
        ('OSCILOBATIENTE', 'Oscilobatiente'),
        ('PAÑO_FIJO', 'Paño Fijo'),
    ]
    
    GLASS_TYPE_CHOICES = [
        ('SIMPLE', 'Simple'),
        ('DVH', 'DVH'),
        ('LAMINADO', 'Laminado'),
    ]
    
    PRICING_METHOD_CHOICES = [
        ('FIXED', 'Precio Fijo'),
        ('AREA', 'Por Área'),
    ]
    
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT)
    uom = models.ForeignKey(UoM, on_delete=models.PROTECT, default=1)
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
    opening_type = models.CharField(max_length=20, choices=OPENING_TYPE_CHOICES)
    glass_type = models.CharField(max_length=20, choices=GLASS_TYPE_CHOICES, blank=True)
    color_code = models.CharField(max_length=20, blank=True)
    width_mm = models.PositiveIntegerField(null=True, blank=True)
    height_mm = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    tax = models.ForeignKey(TaxRate, on_delete=models.PROTECT)
    pricing_method = models.CharField(max_length=10, choices=PRICING_METHOD_CHOICES, default='FIXED')
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price_per_m2 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    min_area_m2 = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('1.00'))
    is_service = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
            models.Index(fields=['category', 'material', 'opening_type']),
        ]
        
    def clean(self):
        if self.width_mm is not None and self.width_mm <= 0:
            raise ValidationError('El ancho debe ser mayor a 0.')
        if self.height_mm is not None and self.height_mm <= 0:
            raise ValidationError('La altura debe ser mayor a 0.')
            
    def save(self, *args, **kwargs):
        if not self.tax_id:
            default_tax = TaxRate.objects.filter(is_default=True).first()
            if default_tax:
                self.tax = default_tax
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.sku} - {self.name}"


class PriceList(models.Model):
    name = models.CharField(max_length=100, unique=True)
    currency = models.CharField(max_length=3, default='ARS')
    is_default = models.BooleanField(default=False)
    active_from = models.DateField(null=True, blank=True)
    active_to = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Lista de Precios'
        verbose_name_plural = 'Listas de Precios'
        
    def clean(self):
        if self.is_default and PriceList.objects.filter(is_default=True).exclude(pk=self.pk).exists():
            raise ValidationError('Solo puede haber una lista de precios por defecto.')
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name


class PriceListRule(models.Model):
    METHOD_CHOICES = [
        ('FIXED', 'Precio Fijo'),
        ('AREA', 'Por Área'),
    ]
    
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, blank=True)
    fixed_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_per_m2 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    min_area_m2 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    discount_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Regla de Lista de Precios'
        verbose_name_plural = 'Reglas de Lista de Precios'
        unique_together = ('price_list', 'product')
        
    def compute_unit_price(self, width_mm=None, height_mm=None):
        method = self.method or self.product.pricing_method
        
        if method == 'FIXED':
            price = self.fixed_price or self.product.base_price
        else:  # AREA
            if width_mm and height_mm:
                area = Decimal(str(width_mm / 1000)) * Decimal(str(height_mm / 1000))
            else:
                area = Decimal('1.0')
            
            min_area = self.min_area_m2 or self.product.min_area_m2
            area = max(area, min_area)
            
            price_per_m2 = self.price_per_m2 or self.product.price_per_m2
            price = price_per_m2 * area
            
        # Aplicar descuento
        discount_factor = Decimal('1') - (self.discount_pct / Decimal('100'))
        final_price = price * discount_factor
        
        return round(final_price, 2)
        
    def __str__(self):
        return f"{self.price_list.name} - {self.product.sku}"