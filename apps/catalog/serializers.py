from rest_framework import serializers
from .models import ProductTemplate, TemplateAttribute, AttributeOption

class AttributeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeOption
        fields = '__all__'

class TemplateAttributeSerializer(serializers.ModelSerializer):
    options = AttributeOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = TemplateAttribute
        fields = '__all__'

class ProductTemplateSerializer(serializers.ModelSerializer):
    attributes = TemplateAttributeSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductTemplate
        fields = '__all__'