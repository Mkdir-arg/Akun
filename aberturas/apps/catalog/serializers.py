from rest_framework import serializers
from .models import (
    CategoriaProducto, SubcategoriaProducto, Producto,
    MedidaProducto, ColorProducto, LineaProducto
)

class SubcategoriaProductoSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = SubcategoriaProducto
        fields = ['id', 'category', 'category_name', 'name', 'code', 'description', 'is_active']

class CategoriaProductoSerializer(serializers.ModelSerializer):
    subcategories = SubcategoriaProductoSerializer(many=True, read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = CategoriaProducto
        fields = ['id', 'name', 'code', 'parent', 'parent_name', 'is_active', 'subcategories']

class MedidaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedidaProducto
        fields = ['id', 'name', 'code', 'is_active']

class ColorProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorProducto
        fields = ['id', 'name', 'code', 'hex_color', 'is_active']

class LineaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineaProducto
        fields = ['id', 'name', 'code', 'description', 'is_active']

class ProductoSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    medida_name = serializers.CharField(source='medida.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True)
    linea_name = serializers.CharField(source='linea.name', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 'sku', 'category', 'category_name', 'subcategory',
            'material', 'opening_type', 'glass_type',
            'medida', 'medida_name', 'color', 'color_name', 'linea', 'linea_name',
            'width_mm', 'height_mm', 'weight_kg', 'tax', 'currency',
            'pricing_method', 'base_price', 'price_per_m2', 'min_area_m2',
            'is_service', 'is_active'
        ]