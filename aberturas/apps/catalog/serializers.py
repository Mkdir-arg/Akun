from rest_framework import serializers
from .models import ProductTemplate, TemplateAttribute, AttributeOption, ProductClass, AttributeType, PricingMode, Producto


class AttributeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeOption
        fields = ['id', 'label', 'code', 'pricing_mode', 'price_value', 'currency', 'order', 'is_default']
        
    def validate_code(self, value):
        attribute = self.context.get('attribute')
        if attribute and AttributeOption.objects.filter(attribute=attribute, code=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("Ya existe una opción con este código en el atributo.")
        return value


class TemplateAttributeSerializer(serializers.ModelSerializer):
    options = AttributeOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = TemplateAttribute
        fields = ['id', 'name', 'code', 'type', 'is_required', 'order', 'rules_json', 'options']
        
    def validate_code(self, value):
        template = self.context.get('template')
        if template and TemplateAttribute.objects.filter(template=template, code=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("Ya existe un atributo con este código en la plantilla.")
        return value


class ProductTemplateSerializer(serializers.ModelSerializer):
    attributes = TemplateAttributeSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductTemplate
        fields = ['id', 'product_class', 'line_name', 'code', 'base_price_net', 'currency', 
                 'requires_dimensions', 'is_active', 'valid_from', 'valid_to', 'version', 
                 'created_at', 'modified_at', 'attributes']
        read_only_fields = ['created_at', 'modified_at', 'version']


class ProductTemplateListSerializer(serializers.ModelSerializer):
    attributes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductTemplate
        fields = ['id', 'product_class', 'line_name', 'code', 'is_active', 'version', 
                 'created_at', 'attributes_count']
        
    def get_attributes_count(self, obj):
        return obj.attributes.count()


class PreviewPricingRequestSerializer(serializers.Serializer):
    selections = serializers.DictField()
    width_mm = serializers.IntegerField(required=False, min_value=1)
    height_mm = serializers.IntegerField(required=False, min_value=1)
    currency = serializers.CharField(max_length=3, default='ARS')
    iva_pct = serializers.DecimalField(max_digits=5, decimal_places=2, default=21.0)


class PreviewPricingResponseSerializer(serializers.Serializer):
    calc = serializers.DictField()
    price = serializers.DictField()
    breakdown = serializers.ListField()
    currency = serializers.CharField()


class ReorderSerializer(serializers.Serializer):
    new_order = serializers.IntegerField(min_value=1)


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['sku', 'category', 'material', 'opening_type', 'color', 'linea', 'base_price', 'is_active']


class AttributeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeOption
        fields = ['id', 'label', 'code', 'pricing_mode', 'price_value', 'currency', 
                 'order', 'is_default', 'swatch_hex', 'icon', 'qty_attr_code']


class TemplateAttributeSerializer(serializers.ModelSerializer):
    options = AttributeOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = TemplateAttribute
        fields = ['id', 'name', 'code', 'type', 'is_required', 'order', 'render_variant',
                 'rules_json', 'min_value', 'max_value', 'step_value', 'unit_label',
                 'min_width', 'max_width', 'min_height', 'max_height', 'step_mm', 
                 'rebaje_vidrio_mm', 'options']


class ProductTemplateSerializer(serializers.ModelSerializer):
    attributes = TemplateAttributeSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductTemplate
        fields = ['id', 'product_class', 'line_name', 'code', 'base_price_net', 
                 'currency', 'requires_dimensions', 'is_active', 'version', 'attributes']


class ProductTemplateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTemplate
        fields = ['id', 'product_class', 'line_name', 'code', 'version', 'is_active', 'created_at']


class PreviewPricingRequestSerializer(serializers.Serializer):
    selections = serializers.JSONField()
    width_mm = serializers.IntegerField(required=False)
    height_mm = serializers.IntegerField(required=False)
    currency = serializers.CharField(default='ARS')
    iva_pct = serializers.DecimalField(max_digits=5, decimal_places=2, default=21.0)


class ReorderSerializer(serializers.Serializer):
    new_order = serializers.IntegerField(min_value=1)