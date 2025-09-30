from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
import json

class ProductTemplate(models.Model):
    PRODUCT_CLASS_CHOICES = [
        ('VENTANA', 'Ventana'),
        ('PUERTA', 'Puerta'),
        ('ACCESORIO', 'Accesorio'),
    ]
    
    product_class = models.CharField(max_length=20, choices=PRODUCT_CLASS_CHOICES)
    line_name = models.CharField(max_length=50)
    code = models.SlugField(max_length=60, unique=True)
    base_price_net = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="ARS")
    requires_dimensions = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
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

class TemplateAttribute(models.Model):
    ATTRIBUTE_TYPE_CHOICES = [
        ('SELECT', 'Select'),
        ('BOOLEAN', 'Boolean'),
        ('NUMBER', 'Number'),
        ('DIMENSIONS_MM', 'Dimensions (mm)'),
        ('QUANTITY', 'Quantity'),
    ]
    
    template = models.ForeignKey(ProductTemplate, related_name="attributes", on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    code = models.SlugField(max_length=60)
    type = models.CharField(max_length=15, choices=ATTRIBUTE_TYPE_CHOICES)
    is_required = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=1)
    
    # Campos para NUMBER/QUANTITY
    min_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    max_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    
    # Campos para DIMENSIONS_MM
    min_width = models.PositiveIntegerField(null=True, blank=True)
    max_width = models.PositiveIntegerField(null=True, blank=True)
    min_height = models.PositiveIntegerField(null=True, blank=True)
    max_height = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = [("template", "code")]
        ordering = ["order", "id"]
        verbose_name = "Atributo de Plantilla"
        verbose_name_plural = "Atributos de Plantilla"

    def __str__(self):
        return f"{self.template.code} - {self.name}"

class AttributeOption(models.Model):
    PRICING_MODE_CHOICES = [
        ('ABS', 'Suma absoluta por ítem'),
        ('PER_M2', 'Precio por m²'),
        ('FACTOR', 'Factor multiplicativo (x)'),
        ('PER_UNIT', 'Precio por unidad'),
    ]
    
    attribute = models.ForeignKey(TemplateAttribute, related_name="options", on_delete=models.CASCADE)
    label = models.CharField(max_length=80)
    code = models.SlugField(max_length=80)
    pricing_mode = models.CharField(max_length=10, choices=PRICING_MODE_CHOICES, default='ABS')
    price_value = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    currency = models.CharField(max_length=3, default="ARS")
    order = models.PositiveSmallIntegerField(default=1)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = [("attribute", "code")]
        ordering = ["order", "id"]
        verbose_name = "Opción de Atributo"
        verbose_name_plural = "Opciones de Atributo"

    def clean(self):
        if self.is_default:
            existing_default = AttributeOption.objects.filter(
                attribute=self.attribute, is_default=True
            ).exclude(pk=self.pk)
            if existing_default.exists():
                raise ValidationError("Solo puede haber una opción por defecto por atributo.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.attribute.name} - {self.label}"