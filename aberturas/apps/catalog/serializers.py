from rest_framework import serializers
from .models import Producto, CategoriaProducto, UnidadMedida, TasaImpuesto, ListaPrecios, ReglaListaPrecios


class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = ['id', 'code', 'name', 'category', 'is_active']


class CategoriaProductoSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = CategoriaProducto
        fields = ['id', 'name', 'code', 'parent', 'parent_name', 'is_active']


class TasaImpuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasaImpuesto
        fields = ['id', 'name', 'rate', 'is_default']


class ListaPreciosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaPrecios
        fields = ['id', 'name', 'currency', 'is_default', 'active_from', 'active_to']


class ProductoSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    uom_name = serializers.CharField(source='uom.name', read_only=True)
    tax_name = serializers.CharField(source='tax.name', read_only=True)
    tax_rate = serializers.DecimalField(source='tax.rate', max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 'sku', 'name', 'category', 'category_name', 'uom', 'uom_name',
            'material', 'opening_type', 'glass_type', 'color_code',
            'width_mm', 'height_mm', 'weight_kg', 'tax', 'tax_name', 'tax_rate',
            'currency', 'pricing_method', 'base_price', 'price_per_m2', 'min_area_m2',
            'is_service', 'is_active'
        ]
        
    def validate_sku(self, value):
        if Producto.objects.filter(sku=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError('Ya existe un producto con este SKU.')
        return value


class ReglaListaPreciosSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = ReglaListaPrecios
        fields = [
            'id', 'price_list', 'product', 'product_name', 'product_sku',
            'method', 'fixed_price', 'price_per_m2', 'min_area_m2',
            'discount_pct', 'valid_from', 'valid_to'
        ]


class ProductoDetailSerializer(ProductoSerializer):
    price_rules = ReglaListaPreciosSerializer(many=True, read_only=True, source='reglalistaprecios_set')
    
    class Meta(ProductoSerializer.Meta):
        fields = ProductoSerializer.Meta.fields + ['price_rules']