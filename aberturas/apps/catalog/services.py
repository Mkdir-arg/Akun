from decimal import Decimal
from typing import Dict, List, Any, Optional
from .models import ProductTemplate, TemplateAttribute, AttributeOption, AttributeType, PricingMode


class PricingCalculatorService:
    def __init__(self, template: ProductTemplate):
        self.template = template
        
    def validate_selections(self, selections: Dict[str, Any]) -> List[str]:
        """Valida las selecciones contra la plantilla"""
        errors = []
        
        # Verificar atributos requeridos
        for attr in self.template.attributes.filter(is_required=True):
            if attr.code not in selections:
                errors.append(f"Atributo requerido '{attr.name}' no está presente")
                continue
                
            selection = selections[attr.code]
            
            # Validar según tipo
            if attr.type == AttributeType.SELECT:
                if not attr.options.filter(code=selection).exists():
                    errors.append(f"Opción '{selection}' no válida para '{attr.name}'")
                    
            elif attr.type == AttributeType.BOOLEAN:
                if not isinstance(selection, bool):
                    errors.append(f"Valor booleano esperado para '{attr.name}'")
                    
            elif attr.type == AttributeType.DIMENSIONS_MM:
                if not isinstance(selection, dict) or 'width_mm' not in selection or 'height_mm' not in selection:
                    errors.append(f"Dimensiones (width_mm, height_mm) requeridas para '{attr.name}'")
                else:
                    width = selection.get('width_mm', 0)
                    height = selection.get('height_mm', 0)
                    
                    if attr.min_width and width < attr.min_width:
                        errors.append(f"Ancho mínimo {attr.min_width}mm para '{attr.name}'")
                    if attr.max_width and width > attr.max_width:
                        errors.append(f"Ancho máximo {attr.max_width}mm para '{attr.name}'")
                    if attr.min_height and height < attr.min_height:
                        errors.append(f"Alto mínimo {attr.min_height}mm para '{attr.name}'")
                    if attr.max_height and height > attr.max_height:
                        errors.append(f"Alto máximo {attr.max_height}mm para '{attr.name}'")
                        
            elif attr.type in [AttributeType.NUMBER, AttributeType.QUANTITY]:
                try:
                    value = Decimal(str(selection))
                    if attr.min_value and value < attr.min_value:
                        errors.append(f"Valor mínimo {attr.min_value} para '{attr.name}'")
                    if attr.max_value and value > attr.max_value:
                        errors.append(f"Valor máximo {attr.max_value} para '{attr.name}'")
                except (ValueError, TypeError):
                    errors.append(f"Valor numérico esperado para '{attr.name}'")
        
        return errors
    
    def calculate_preview_pricing(self, selections: Dict[str, Any], width_mm: Optional[int] = None, 
                                height_mm: Optional[int] = None, currency: str = 'ARS', 
                                iva_pct: Decimal = Decimal('21.0')) -> Dict[str, Any]:
        """Calcula el preview de precios según las especificaciones"""
        
        # Inicializar cálculos
        calc = {}
        breakdown = []
        
        # Precio base
        net_price = self.template.base_price_net
        if net_price > 0:
            breakdown.append({
                'source': 'template_base',
                'mode': 'ABS',
                'value': float(net_price)
            })
        
        # Calcular dimensiones
        dimensions_attr = self.template.attributes.filter(type=AttributeType.DIMENSIONS_MM).first()
        if dimensions_attr:
            dim_data = selections.get(dimensions_attr.code, {})
            if isinstance(dim_data, dict):
                width = dim_data.get('width_mm', width_mm or 0)
                height = dim_data.get('height_mm', height_mm or 0)
            else:
                width = width_mm or 0
                height = height_mm or 0
                
            if width and height:
                calc['area_m2'] = round((width * height) / 1_000_000, 4)
                calc['perimeter_m'] = round(2 * (width + height) / 1000, 4)
        
        # Acumuladores por tipo de precio
        abs_total = net_price
        per_unit_total = Decimal('0')
        per_m2_total = Decimal('0')
        perimeter_total = Decimal('0')
        factors = []
        
        # Procesar selecciones
        for attr in self.template.attributes.all():
            if attr.code not in selections:
                continue
                
            selection = selections[attr.code]
            
            if attr.type == AttributeType.SELECT:
                option = attr.options.filter(code=selection).first()
                if option:
                    self._apply_option_pricing(option, calc, selections, breakdown,
                                             abs_total, per_unit_total, per_m2_total,
                                             perimeter_total, factors)
            
            elif attr.type == AttributeType.BOOLEAN and selection:
                # Precio a nivel atributo para BOOLEAN
                pricing_mode = attr.rules_json.get('pricing_mode')
                if pricing_mode:
                    price_value = Decimal(str(attr.rules_json.get('price_value', 0)))
                    
                    if pricing_mode == 'ABS':
                        abs_total += price_value
                        breakdown.append({
                            'source': f'{attr.code}/true',
                            'mode': 'ABS',
                            'value': float(price_value)
                        })
                    elif pricing_mode == 'PER_M2' and 'area_m2' in calc:
                        total = price_value * Decimal(str(calc['area_m2']))
                        per_m2_total += total
                        breakdown.append({
                            'source': f'{attr.code}/true',
                            'mode': 'PER_M2',
                            'm2': calc['area_m2'],
                            'unit': float(price_value),
                            'value': float(total)
                        })
                    elif pricing_mode == 'PERIMETER' and 'perimeter_m' in calc:
                        total = price_value * Decimal(str(calc['perimeter_m']))
                        perimeter_total += total
                        breakdown.append({
                            'source': f'{attr.code}/true',
                            'mode': 'PERIMETER',
                            'm': calc['perimeter_m'],
                            'unit': float(price_value),
                            'value': float(total)
                        })
        
        # Sumar componentes antes de factores
        subtotal = abs_total + per_unit_total + per_m2_total + perimeter_total
        
        # Aplicar factores
        for factor_info in factors:
            delta = subtotal * (factor_info['factor'] - Decimal('1'))
            subtotal += delta
            breakdown.append({
                'source': factor_info['source'],
                'mode': 'FACTOR',
                'factor': float(factor_info['factor']),
                'applied_on': float(subtotal - delta),
                'delta': float(delta)
            })
        
        # Calcular impuestos
        tax = subtotal * (iva_pct / Decimal('100'))
        gross = subtotal + tax
        
        return {
            'calc': calc,
            'price': {
                'net': float(subtotal),
                'tax': float(tax),
                'gross': float(gross)
            },
            'breakdown': breakdown,
            'currency': currency
        }
    
    def _apply_option_pricing(self, option: AttributeOption, calc: Dict, selections: Dict,
                            breakdown: List, abs_total: Decimal, per_unit_total: Decimal,
                            per_m2_total: Decimal, perimeter_total: Decimal, factors: List):
        """Aplica el pricing de una opción según su modo"""
        price_value = option.price_value
        
        if option.pricing_mode == PricingMode.ABS:
            abs_total += price_value
            breakdown.append({
                'source': f'{option.attribute.code}/{option.code}',
                'mode': 'ABS',
                'value': float(price_value)
            })
        
        elif option.pricing_mode == PricingMode.PER_UNIT and option.qty_attr_code:
            qty = selections.get(option.qty_attr_code, 0)
            total = price_value * Decimal(str(qty))
            per_unit_total += total
            breakdown.append({
                'source': f'{option.attribute.code}/{option.code}',
                'mode': 'PER_UNIT',
                'qty_attr': option.qty_attr_code,
                'qty': qty,
                'unit': float(price_value),
                'value': float(total)
            })
        
        elif option.pricing_mode == PricingMode.PER_M2 and 'area_m2' in calc:
            total = price_value * Decimal(str(calc['area_m2']))
            per_m2_total += total
            breakdown.append({
                'source': f'{option.attribute.code}/{option.code}',
                'mode': 'PER_M2',
                'm2': calc['area_m2'],
                'unit': float(price_value),
                'value': float(total)
            })
        
        elif option.pricing_mode == PricingMode.PERIMETER and 'perimeter_m' in calc:
            total = price_value * Decimal(str(calc['perimeter_m']))
            perimeter_total += total
            breakdown.append({
                'source': f'{option.attribute.code}/{option.code}',
                'mode': 'PERIMETER',
                'm': calc['perimeter_m'],
                'unit': float(price_value),
                'value': float(total)
            })
        
        elif option.pricing_mode == PricingMode.FACTOR:
            factors.append({
                'source': f'{option.attribute.code}/{option.code}',
                'factor': price_value
            })