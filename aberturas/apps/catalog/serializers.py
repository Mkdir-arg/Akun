from rest_framework import serializers
from .models import Product, ProductCategory, UoM, TaxRate, PriceList, PriceListRule


class UoMSerializer(serializers.ModelSerializer):
    class Meta:
        model = UoM
        fields = ['id', 'code', 'name', 'category', 'is_active']


class ProductCategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'code', 'parent', 'parent_name', 'is_active']


class TaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRate
        fields = ['id', 'name', 'rate', 'is_default']


class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = ['id', 'name', 'currency', 'is_default', 'active_from', 'active_to']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    uom_name = serializers.CharField(source='uom.name', read_only=True)
    tax_name = serializers.CharField(source='tax.name', read_only=True)
    tax_rate = serializers.DecimalField(source='tax.rate', max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'category', 'category_name', 'uom', 'uom_name',
            'material', 'opening_type', 'glass_type', 'color_code',
            'width_mm', 'height_mm', 'weight_kg', 'tax', 'tax_name', 'tax_rate',
            'currency', 'pricing_method', 'base_price', 'price_per_m2', 'min_area_m2',
            'is_service', 'is_active'
        ]
        
    def validate_sku(self, value):
        if Product.objects.filter(sku=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError('Ya existe un producto con este SKU.')
        return value


class PriceListRuleSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = PriceListRule
        fields = [
            'id', 'price_list', 'product', 'product_name', 'product_sku',
            'method', 'fixed_price', 'price_per_m2', 'min_area_m2',
            'discount_pct', 'valid_from', 'valid_to'
        ]


class ProductDetailSerializer(ProductSerializer):
    price_rules = PriceListRuleSerializer(many=True, read_only=True, source='pricelistrule_set')
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['price_rules']