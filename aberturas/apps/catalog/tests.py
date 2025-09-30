from django.test import TestCase
from decimal import Decimal
from .models import ProductTemplate, TemplateAttribute, AttributeOption, ProductClass, AttributeType, PricingMode
from .services import PricingCalculatorService


class PricingCalculatorServiceTest(TestCase):
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear plantilla
        self.template = ProductTemplate.objects.create(
            product_class=ProductClass.VENTANA,
            line_name="Módena",
            code="ventana-modena",
            base_price_net=Decimal('50000.00'),
            requires_dimensions=True
        )
        
        # Crear atributos
        self.attr_hojas = TemplateAttribute.objects.create(
            template=self.template,
            name="Hojas",
            code="hojas",
            type=AttributeType.SELECT,
            order=1
        )
        
        self.attr_color = TemplateAttribute.objects.create(
            template=self.template,
            name="Color",
            code="color",
            type=AttributeType.SELECT,
            order=2
        )
        
        self.attr_contramarco = TemplateAttribute.objects.create(
            template=self.template,
            name="Contramarco",
            code="contramarco",
            type=AttributeType.BOOLEAN,
            is_required=False,
            order=3
        )
        
        self.attr_vidrio = TemplateAttribute.objects.create(
            template=self.template,
            name="Vidrio",
            code="vidrio",
            type=AttributeType.SELECT,
            order=4
        )
        
        # Crear opciones
        AttributeOption.objects.create(
            attribute=self.attr_hojas,
            label="1 hoja",
            code="1h",
            pricing_mode=PricingMode.ABS,
            price_value=Decimal('0'),
            is_default=True
        )
        
        AttributeOption.objects.create(
            attribute=self.attr_hojas,
            label="2 hojas",
            code="2h",
            pricing_mode=PricingMode.ABS,
            price_value=Decimal('12000')
        )
        
        AttributeOption.objects.create(
            attribute=self.attr_color,
            label="Blanco",
            code="blanco",
            pricing_mode=PricingMode.ABS,
            price_value=Decimal('0'),
            is_default=True
        )
        
        AttributeOption.objects.create(
            attribute=self.attr_color,
            label="Negro Mate",
            code="negro-mate",
            pricing_mode=PricingMode.FACTOR,
            price_value=Decimal('1.08')
        )
        
        AttributeOption.objects.create(
            attribute=self.attr_contramarco,
            label="Con contramarco",
            code="true",
            pricing_mode=PricingMode.PERIMETER,
            price_value=Decimal('1500')
        )
        
        AttributeOption.objects.create(
            attribute=self.attr_vidrio,
            label="Float 4mm",
            code="float-4mm",
            pricing_mode=PricingMode.PER_M2,
            price_value=Decimal('8900'),
            is_default=True
        )
        
    def test_calculate_dimensions(self):
        """Test cálculo de dimensiones"""
        calculator = PricingCalculatorService(self.template)
        
        calc_data = calculator._calculate_dimensions(1300, 1200)
        
        self.assertEqual(calc_data['area_m2'], 1.56)
        self.assertEqual(calc_data['perimeter_m'], 5.0)
        
    def test_basic_pricing_calculation(self):
        """Test cálculo básico de precio"""
        calculator = PricingCalculatorService(self.template)
        
        selections = {
            'hojas': '2h',
            'color': 'negro-mate',
            'contramarco': True,
            'vidrio': 'float-4mm'
        }
        
        result = calculator.calculate_preview_pricing(
            selections=selections,
            width_mm=1300,
            height_mm=1200,
            iva_pct=Decimal('21.0')
        )
        
        # Verificar estructura de respuesta
        self.assertIn('calc', result)
        self.assertIn('price', result)
        self.assertIn('breakdown', result)
        self.assertIn('currency', result)
        
        # Verificar cálculos
        self.assertEqual(result['calc']['area_m2'], 1.56)
        self.assertEqual(result['calc']['perimeter_m'], 5.0)
        
        # Verificar que el precio neto sea correcto
        # Base: 50000 + Hojas: 12000 + Vidrio: 8900*1.56 + Contramarco: 1500*5.0 = 83384
        # Factor color negro: 83384 * 1.08 = 90054.72
        expected_net = 90054.72
        self.assertAlmostEqual(result['price']['net'], expected_net, places=2)
        
        # Verificar IVA
        expected_tax = expected_net * 0.21
        self.assertAlmostEqual(result['price']['tax'], expected_tax, places=2)
        
    def test_validation_required_dimensions(self):
        """Test validación de dimensiones requeridas"""
        calculator = PricingCalculatorService(self.template)
        
        selections = {'hojas': '1h', 'color': 'blanco', 'vidrio': 'float-4mm'}
        
        with self.assertRaises(ValueError):
            calculator.calculate_preview_pricing(selections=selections)
            
    def test_validate_selections(self):
        """Test validación de selecciones"""
        calculator = PricingCalculatorService(self.template)
        
        # Selecciones válidas
        valid_selections = {
            'hojas': '1h',
            'color': 'blanco',
            'vidrio': 'float-4mm'
        }
        errors = calculator.validate_selections(valid_selections)
        self.assertEqual(len(errors), 0)
        
        # Selecciones inválidas - falta atributo requerido
        invalid_selections = {
            'hojas': '1h',
            'color': 'blanco'
            # Falta vidrio que es requerido
        }
        errors = calculator.validate_selections(invalid_selections)
        self.assertGreater(len(errors), 0)
        
        # Opción inexistente
        invalid_selections = {
            'hojas': 'inexistente',
            'color': 'blanco',
            'vidrio': 'float-4mm'
        }
        errors = calculator.validate_selections(invalid_selections)
        self.assertGreater(len(errors), 0)
        
    def test_boolean_attribute_handling(self):
        """Test manejo de atributos booleanos"""
        calculator = PricingCalculatorService(self.template)
        
        selections = {
            'hojas': '1h',
            'color': 'blanco',
            'contramarco': True,  # Boolean true
            'vidrio': 'float-4mm'
        }
        
        result = calculator.calculate_preview_pricing(
            selections=selections,
            width_mm=1000,
            height_mm=1000,
            iva_pct=Decimal('21.0')
        )
        
        # Debe incluir el costo del contramarco
        contramarco_cost = 1500 * 4.0  # perímetro de 1000x1000 = 4m
        self.assertTrue(any(
            item['source'] == 'contramarco/true' 
            for item in result['breakdown']
        ))
        
    def test_factor_pricing_mode(self):
        """Test modo de precio por factor"""
        calculator = PricingCalculatorService(self.template)
        
        selections = {
            'hojas': '1h',
            'color': 'negro-mate',  # Factor 1.08
            'vidrio': 'float-4mm'
        }
        
        result = calculator.calculate_preview_pricing(
            selections=selections,
            width_mm=1000,
            height_mm=1000,
            iva_pct=Decimal('21.0')
        )
        
        # Buscar el item del factor en el breakdown
        factor_item = next(
            (item for item in result['breakdown'] if item['source'] == 'color/negro-mate'),
            None
        )
        
        self.assertIsNotNone(factor_item)
        self.assertEqual(factor_item['mode'], 'FACTOR')
        self.assertEqual(factor_item['factor'], 1.08)