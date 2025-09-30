from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from decimal import Decimal
import json


class MedidaProducto(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Medida de Producto'
        verbose_name_plural = 'Medidas de Producto'
        
    def __str__(self):
        return self.name


class ColorProducto(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    hex_color = models.CharField(max_length=7, blank=True, help_text='Color en formato hexadecimal (#FFFFFF)')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Color de Producto'
        verbose_name_plural = 'Colores de Producto'
        
    def __str__(self):
        return self.name


class LineaProducto(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Línea de Producto'
        verbose_name_plural = 'Líneas de Producto'
        
    def __str__(self):
        return self.name


class UnidadMedida(models.Model):
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


class CategoriaProducto(models.Model):
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


class SubcategoriaProducto(models.Model):
    category = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    code = models.SlugField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Subcategoría de Producto'
        verbose_name_plural = 'Subcategorías de Producto'
        unique_together = ('category', 'code')
        
    def __str__(self):
        return f"{self.category.name} - {self.name}"


class TasaImpuesto(models.Model):
    name = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Tasa de Impuesto'
        verbose_name_plural = 'Tasas de Impuesto'
        
    def clean(self):
        if self.is_default and TasaImpuesto.objects.filter(is_default=True).exclude(pk=self.pk).exists():
            raise ValidationError('Solo puede haber una tasa de impuesto por defecto.')
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name


class Producto(models.Model):
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
    
    # Subcategorías por categoría
    SUBCATEGORY_CHOICES = {
        'ventanas': [
            ('CORREDIZA_SIMPLE', 'Corrediza Simple'),
            ('CORREDIZA_DOBLE', 'Corrediza Doble'),
            ('BATIENTE_SIMPLE', 'Batiente Simple'),
            ('BATIENTE_DOBLE', 'Batiente Doble'),
            ('OSCILOBATIENTE', 'Oscilobatiente'),
            ('PAÑO_FIJO', 'Paño Fijo'),
        ],
        'puertas': [
            ('ENTRADA_PRINCIPAL', 'Entrada Principal'),
            ('BALCON', 'Balcón'),
            ('INTERIOR', 'Interior'),
            ('PLEGADIZA', 'Plegadiza'),
        ],
        'portones': [
            ('CORREDIZO', 'Corredizo'),
            ('LEVADIZO', 'Levadizo'),
            ('BATIENTE', 'Batiente'),
        ],
        'accesorios': [
            ('HERRAJES', 'Herrajes'),
            ('VIDRIOS', 'Vidrios'),
            ('PERFILES', 'Perfiles'),
            ('SELLADORES', 'Selladores'),
        ],
        'herrajes': [
            ('CERRADURAS', 'Cerraduras'),
            ('BISAGRAS', 'Bisagras'),
            ('MANIJAS', 'Manijas'),
            ('RIELES', 'Rieles'),
        ],
    }
    
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    category = models.ForeignKey(CategoriaProducto, on_delete=models.PROTECT)
    subcategory = models.CharField(max_length=100, blank=True, null=True)
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
    opening_type = models.CharField(max_length=20, choices=OPENING_TYPE_CHOICES)
    glass_type = models.CharField(max_length=20, choices=GLASS_TYPE_CHOICES, blank=True)

    color = models.ForeignKey(ColorProducto, on_delete=models.PROTECT, default=1)
    linea = models.ForeignKey(LineaProducto, on_delete=models.PROTECT, default=1)
    width_mm = models.PositiveIntegerField(null=True, blank=True)
    height_mm = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    tax = models.ForeignKey(TasaImpuesto, on_delete=models.PROTECT)
    currency = models.ForeignKey('core.Moneda', on_delete=models.PROTECT, default=1)
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
            models.Index(fields=['category', 'material', 'opening_type']),
            models.Index(fields=['color', 'linea']),
        ]
        
    def clean(self):
        if self.width_mm is not None and self.width_mm <= 0:
            raise ValidationError('El ancho debe ser mayor a 0.')
        if self.height_mm is not None and self.height_mm <= 0:
            raise ValidationError('La altura debe ser mayor a 0.')
            
    def save(self, *args, **kwargs):
        if not self.tax_id:
            default_tax = TasaImpuesto.objects.filter(is_default=True).first()
            if default_tax:
                self.tax = default_tax
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.sku} - {self.color.name} {self.linea.name}"


class ListaPrecios(models.Model):
    name = models.CharField(max_length=100, unique=True)
    currency = models.CharField(max_length=3, default='ARS')
    is_default = models.BooleanField(default=False)
    active_from = models.DateField(null=True, blank=True)
    active_to = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Lista de Precios'
        verbose_name_plural = 'Listas de Precios'
        
    def clean(self):
        if self.is_default and ListaPrecios.objects.filter(is_default=True).exclude(pk=self.pk).exists():
            raise ValidationError('Solo puede haber una lista de precios por defecto.')
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name


class ReglaListaPrecios(models.Model):
    METHOD_CHOICES = [
        ('FIXED', 'Precio Fijo'),
        ('AREA', 'Por Área'),
    ]
    
    price_list = models.ForeignKey(ListaPrecios, on_delete=models.CASCADE)
    product = models.ForeignKey(Producto, on_delete=models.CASCADE)
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


# ============ NUEVOS MODELOS PARA PLANTILLAS ============

class ProductClass(models.TextChoices):
    VENTANA = "VENTANA", "Ventana"
    PUERTA = "PUERTA", "Puerta"
    ACCESORIO = "ACCESORIO", "Accesorio"


class ProductTemplate(models.Model):
    product_class = models.CharField(max_length=20, choices=ProductClass.choices)
    line_name = models.CharField(max_length=50)  # p.ej. "Módena"
    code = models.SlugField(max_length=60, unique=True)  # p.ej. ventana-modena
    base_price_net = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # opcional
    currency = models.CharField(max_length=3, default="ARS")
    requires_dimensions = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("line_name", "version")]
        verbose_name = "Plantilla de Producto"
        verbose_name_plural = "Plantillas de Producto"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product_class} - {self.line_name} v{self.version}"


class AttributeType(models.TextChoices):
    SELECT = "SELECT", "Select"
    BOOLEAN = "BOOLEAN", "Boolean"
    NUMBER = "NUMBER", "Number"
    DIMENSIONS_MM = "DIMENSIONS_MM", "Dimensions (mm)"
    QUANTITY = "QUANTITY", "Quantity"


class RenderVariant(models.TextChoices):
    SELECT = "select", "Select"
    SWATCHES = "swatches", "Swatches"
    RADIO = "radio", "Radio"
    BUTTONS = "buttons", "Buttons"


class TemplateAttribute(models.Model):
    template = models.ForeignKey(ProductTemplate, related_name="attributes", on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    code = models.SlugField(max_length=60)
    type = models.CharField(max_length=15, choices=AttributeType.choices)
    is_required = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=1)
    render_variant = models.CharField(max_length=10, choices=RenderVariant.choices, default=RenderVariant.SELECT)
    rules_json = models.JSONField(default=dict, blank=True)
    
    # Campos para NUMBER/QUANTITY
    min_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    max_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    step_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    unit_label = models.CharField(max_length=20, blank=True)
    
    # Campos para DIMENSIONS_MM
    min_width = models.PositiveIntegerField(null=True, blank=True)
    max_width = models.PositiveIntegerField(null=True, blank=True)
    min_height = models.PositiveIntegerField(null=True, blank=True)
    max_height = models.PositiveIntegerField(null=True, blank=True)
    step_mm = models.PositiveIntegerField(default=10, null=True, blank=True)
    rebaje_vidrio_mm = models.PositiveIntegerField(default=0, null=True, blank=True)

    class Meta:
        unique_together = [("template", "code")]
        ordering = ["order", "id"]
        verbose_name = "Atributo de Plantilla"
        verbose_name_plural = "Atributos de Plantilla"

    def __str__(self):
        return f"{self.template.code} - {self.name}"


class PricingMode(models.TextChoices):
    ABS = "ABS", "Suma absoluta por ítem"
    PER_M2 = "PER_M2", "Precio por m²"
    PERIMETER = "PERIMETER", "Precio por perímetro (m)"
    FACTOR = "FACTOR", "Factor multiplicativo (x)"
    PER_UNIT = "PER_UNIT", "Precio por unidad"


class AttributeOption(models.Model):
    attribute = models.ForeignKey(TemplateAttribute, related_name="options", on_delete=models.CASCADE)
    label = models.CharField(max_length=80)
    code = models.SlugField(max_length=80)
    pricing_mode = models.CharField(max_length=10, choices=PricingMode.choices, default=PricingMode.ABS)
    price_value = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    currency = models.CharField(max_length=3, default="ARS")
    order = models.PositiveSmallIntegerField(default=1)
    is_default = models.BooleanField(default=False)
    
    # Visual
    swatch_hex = models.CharField(max_length=7, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    
    # Para PER_UNIT
    qty_attr_code = models.CharField(max_length=60, blank=True)

    class Meta:
        unique_together = [("attribute", "code")]
        ordering = ["order", "id"]
        verbose_name = "Opción de Atributo"
        verbose_name_plural = "Opciones de Atributo"

    def clean(self):
        # Validar que solo haya una opción por defecto por atributo
        if self.is_default:
            existing_default = AttributeOption.objects.filter(
                attribute=self.attribute, is_default=True
            ).exclude(pk=self.pk)
            if existing_default.exists():
                raise ValidationError("Solo puede haber una opción por defecto por atributo.")
        
        # Validar PER_UNIT requiere qty_attr_code
        if self.pricing_mode == PricingMode.PER_UNIT and not self.qty_attr_code:
            raise ValidationError("PER_UNIT requiere especificar qty_attr_code.")
        
        # Validar que qty_attr_code existe y es QUANTITY
        if self.qty_attr_code:
            try:
                qty_attr = TemplateAttribute.objects.get(
                    template=self.attribute.template,
                    code=self.qty_attr_code,
                    type=AttributeType.QUANTITY
                )
            except TemplateAttribute.DoesNotExist:
                raise ValidationError(f"No existe atributo QUANTITY con code '{self.qty_attr_code}' en esta plantilla.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.attribute.name} - {self.label}"