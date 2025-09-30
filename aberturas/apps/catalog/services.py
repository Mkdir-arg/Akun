from decimal import Decimal
from typing import Dict, Any, List
from django.core.exceptions import ValidationError

from .models import (
    ProductTemplate, TemplateAttribute, AttributeOption,
    AttributeType, PricingMode
)


class PricingCalculatorService:
    def __init__(self, template: ProductTemplate):
        self.template = template
        
    def validate_selections(self, selections: Dict[str, Any]) -> List[str]:
        """Valida las selecciones del usuario"""
        errors = []
        
        # Verificar atributos requeridos
        for attr in self.template.attributes.filter(is_required=True):
            if attr.code not in selections or selections[attr.code] is None:
                errors.append(f"El atributo '{attr.name}' es requerido")
                continue
                
            # Validaciones específicas por tipo
            if attr.type == AttributeType.SELECT:
                if not attr.options.filter(code=selections[attr.code]).exists():
                    errors.append(f"Opción inválida para '{attr.name}'")
                    
            elif attr.type == AttributeType.DIMENSIONS_MM:
                dim = selections[attr.code]
                if not isinstance(dim, dict) or 'width_mm' not in dim or 'height_mm' not in dim:
                    errors.append(f"Dimensiones inválidas para '{attr.name}'")
                else:
                    width = dim.get('width_mm', 0)
                    height = dim.get('height_mm', 0)
                    
                    if attr.min_width and width < attr.min_width:
                        errors.append(f"Ancho mínimo para '{attr.name}': {attr.min_width}mm")
                    if attr.max_width and width > attr.max_width:
                        errors.append(f"Ancho máximo para '{attr.name}': {attr.max_width}mm")
                    if attr.min_height and height < attr.min_height:
                        errors.append(f"Alto mínimo para '{attr.name}': {attr.min_height}mm")
                    if attr.max_height and height > attr.max_height:
                        errors.append(f"Alto máximo para '{attr.name}': {attr.max_height}mm")
                        
            elif attr.type in [AttributeType.NUMBER, AttributeType.QUANTITY]:
                value = selections[attr.code]
                if not isinstance(value, (int, float)):
                    errors.append(f"Valor numérico inválido para '{attr.name}'")
                else:
                    if attr.min_value and value < attr.min_value:
                        errors.append(f"Valor mínimo para '{attr.name}': {attr.min_value}")
                    if attr.max_value and value > attr.max_value:
                        errors.append(f"Valor máximo para '{attr.name}': {attr.max_value}")
        
        # Validar que existan dimensiones si hay precios PER_M2 o PERIMETER
        has_area_pricing = False
        has_perimeter_pricing = False
        
        for attr in self.template.attributes.all():
            if attr.type == AttributeType.SELECT:
                for option in attr.options.all():
                    if option.pricing_mode == PricingMode.PER_M2:
                        has_area_pricing = True
                    elif option.pricing_mode == PricingMode.PERIMETER:
                        has_perimeter_pricing = True
            elif attr.type == AttributeType.BOOLEAN:
                pricing_info = attr.rules_json.get('pricing', {})
                mode = pricing_info.get('pricing_mode')
                if mode == 'PER_M2':
                    has_area_pricing = True
                elif mode == 'PERIMETER':
                    has_perimeter_pricing = True
        
        if (has_area_pricing or has_perimeter_pricing):
            dim_attr = self.template.attributes.filter(type=AttributeType.DIMENSIONS_MM).first()
            if not dim_attr:
                errors.append("Se requiere un atributo DIMENSIONS_MM para precios por área/perímetro")
            elif dim_attr.code not in selections:
                errors.append("Se requieren dimensiones para calcular el precio")
                
        return errors
    
    def calculate_preview_pricing(self, selections: Dict[str, Any], width_mm: int = None, 
                                height_mm: int = None, currency: str = "ARS", 
                                iva_pct: Decimal = Decimal('21.0')) -> Dict[str, Any]:
        """Calcula el precio de preview"""
        
        # Inicializar cálculos
        calc = {}
        price_net = Decimal(str(self.template.base_price_net))
        breakdown = []
        
        if self.template.base_price_net > 0:
            breakdown.append({
                "source": "template_base",
                "mode": "ABS",
                "value": float(self.template.base_price_net)
            })
        
        # Obtener dimensiones
        dimensions = selections.get('dim') or {}
        if width_mm:
            dimensions['width_mm'] = width_mm
        if height_mm:
            dimensions['height_mm'] = height_mm
            
        if dimensions.get('width_mm') and dimensions.get('height_mm'):
            width = dimensions['width_mm']
            height = dimensions['height_mm']
            calc['area_m2'] = round((width * height) / 1_000_000, 4)
            calc['perimeter_m'] = round(2 * (width + height) / 1000, 4)
        
        # Procesar atributos en orden: ABS, PER_UNIT, PER_M2, PERIMETER, luego FACTOR
        attributes = self.template.attributes.all().order_by('order')
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
                        value = self._calculate_option_price(option, selections, calc)
                        if value > 0:
                            price_net += Decimal(str(value))
                            breakdown.append({
                                "source": f"{attr_code}/{option.code}",
                                "mode": option.pricing_mode,
                                "value": float(value),
                                **self._get_breakdown_details(option, selections, calc)
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
                            "value": float(value),
                            **({"m2": calc['area_m2'], "unit": float(price_val)} if mode == 'PER_M2' else {}),
                            **({"m": calc['perimeter_m'], "unit": float(price_val)} if mode == 'PERIMETER' else {})
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
        tax = price_net * (iva_pct / Decimal('100'))
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
    
    def _calculate_option_price(self, option: AttributeOption, selections: Dict, calc: Dict) -> Decimal:
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
    
    def _get_breakdown_details(self, option: AttributeOption, selections: Dict, calc: Dict) -> Dict:
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