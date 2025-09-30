from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
import json
from typing import Dict, Any


# ============ MODELOS PARA PLANTILLAS ============

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

    @classmethod
    def calculate_pricing(cls, template_id: int, selections: Dict[str, Any], currency: str = "ARS", iva_pct: float = 21.0) -> Dict[str, Any]:
        """Calcula el precio basado en las selecciones del usuario"""
        from decimal import Decimal
        
        try:
            template = ProductTemplate.objects.get(id=template_id)
        except ProductTemplate.DoesNotExist:
            raise ValidationError(f"Template {template_id} no existe")
        
        # Inicializar cálculos
        calc = {}
        price_net = Decimal(str(template.base_price_net))
        breakdown = []
        
        if template.base_price_net > 0:
            breakdown.append({
                "source": "template_base",
                "mode": "ABS",
                "value": float(template.base_price_net)
            })
        
        # Obtener dimensiones si existen
        dimensions = selections.get('dim', {})
        if dimensions:
            width_mm = dimensions.get('width_mm', 0)
            height_mm = dimensions.get('height_mm', 0)
            if width_mm and height_mm:
                calc['area_m2'] = round((width_mm * height_mm) / 1_000_000, 4)
                calc['perimeter_m'] = round(2 * (width_mm + height_mm) / 1000, 4)
        
        # Procesar atributos en orden: ABS, PER_UNIT, PER_M2, PERIMETER, luego FACTOR
        attributes = template.attributes.all().order_by('order')
        factor_items = []
        
        for attr in attributes:
            attr_code = attr.code
            selection = selections.get(attr_code)
            
            if selection is None:
                continue
                
            if attr.type == AttributeType.SELECT:
                try:
                    option = attr.options.get(code=selection)
                    
                    if option.pricing_mode == PricingMode.FACTOR:
                        factor_items.append(option)
                    else:
                        value = cls._calculate_option_price(option, selections, calc)
                        if value > 0:
                            price_net += Decimal(str(value))
                            breakdown.append({
                                "source": f"{attr_code}/{option.code}",
                                "mode": option.pricing_mode,
                                "value": float(value),
                                **cls._get_breakdown_details(option, selections, calc)
                            })
                            
                except AttributeOption.DoesNotExist:
                    continue
                    
            elif attr.type == AttributeType.BOOLEAN and selection:
                # Precio a nivel atributo para BOOLEAN
                pricing_info = attr.rules_json.get('pricing', {})
                if pricing_info:
                    mode = pricing_info.get('pricing_mode')
                    price_val = Decimal(str(pricing_info.get('price_value', 0)))
                    
                    if mode == 'ABS':
                        value = price_val
                    elif mode == 'PER_M2' and calc.get('area_m2'):
                        value = price_val * Decimal(str(calc['area_m2']))
                    elif mode == 'PERIMETER' and calc.get('perimeter_m'):
                        value = price_val * Decimal(str(calc['perimeter_m']))
                    else:
                        value = Decimal('0')
                    
                    if value > 0:
                        price_net += value
                        breakdown.append({
                            "source": f"{attr_code}/true",
                            "mode": mode,
                            "value": float(value)
                        })
        
        # Aplicar factores al final
        for option in factor_items:
            factor = Decimal(str(option.price_value))
            applied_on = price_net
            delta = applied_on * (factor - Decimal('1'))
            price_net += delta
            
            breakdown.append({
                "source": f"{option.attribute.code}/{option.code}",
                "mode": "FACTOR",
                "factor": float(factor),
                "applied_on": float(applied_on),
                "delta": float(delta)
            })
        
        # Calcular impuestos
        tax = price_net * (Decimal(str(iva_pct)) / Decimal('100'))
        price_gross = price_net + tax
        
        return {
            "calc": calc,
            "price": {
                "net": float(price_net),
                "tax": float(tax),
                "gross": float(price_gross)
            },
            "breakdown": breakdown,
            "currency": currency
        }
    
    @classmethod
    def _calculate_option_price(cls, option, selections: Dict, calc: Dict) -> Decimal:
        """Calcula el precio de una opción específica"""
        price_val = Decimal(str(option.price_value))
        
        if option.pricing_mode == PricingMode.ABS:
            return price_val
        elif option.pricing_mode == PricingMode.PER_M2:
            area = calc.get('area_m2', 0)
            return price_val * Decimal(str(area)) if area else Decimal('0')
        elif option.pricing_mode == PricingMode.PERIMETER:
            perimeter = calc.get('perimeter_m', 0)
            return price_val * Decimal(str(perimeter)) if perimeter else Decimal('0')
        elif option.pricing_mode == PricingMode.PER_UNIT:
            qty = selections.get(option.qty_attr_code, 0)
            return price_val * Decimal(str(qty)) if qty else Decimal('0')
        
        return Decimal('0')
    
    @classmethod
    def _get_breakdown_details(cls, option, selections: Dict, calc: Dict) -> Dict:
        """Obtiene detalles adicionales para el breakdown"""
        details = {}
        
        if option.pricing_mode == PricingMode.PER_M2:
            details.update({
                "m2": calc.get('area_m2', 0),
                "unit": float(option.price_value)
            })
        elif option.pricing_mode == PricingMode.PERIMETER:
            details.update({
                "m": calc.get('perimeter_m', 0),
                "unit": float(option.price_value)
            })
        elif option.pricing_mode == PricingMode.PER_UNIT:
            qty = selections.get(option.qty_attr_code, 0)
            details.update({
                "qty_attr": option.qty_attr_code,
                "qty": qty,
                "unit": float(option.price_value)
            })
        
        return details