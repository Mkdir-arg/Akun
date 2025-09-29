from rest_framework import serializers
from .models import CategoriaProducto, SubcategoriaProducto, Producto

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

class ProductoSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Producto
        fields = ['id', 'sku', 'name', 'category', 'category_name', 'material', 'opening_type', 'is_active']