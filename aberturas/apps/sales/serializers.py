from rest_framework import serializers
from .models import Quote, QuoteItem, Order, OrderItem
from apps.crm.serializers import CustomerSerializer
from apps.catalog.serializers import ProductSerializer


class QuoteItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = QuoteItem
        fields = [
            'id', 'quote', 'product', 'product_name', 'product_sku',
            'description', 'width_mm', 'height_mm',
            'quantity', 'unit_price', 'discount_pct', 'tax_rate',
            'subtotal', 'discount_amount', 'tax_amount', 'total',
            'line_number', 'assigned_to', 'assigned_to_name'
        ]
        read_only_fields = ['subtotal', 'discount_amount', 'tax_amount', 'total']
    
    def validate(self, data):
        print(f"DEBUG - Validating data: {data}")
        if 'quote' not in data or data['quote'] is None:
            raise serializers.ValidationError('Quote is required')
        # Para servicios, product puede ser null
        if data.get('product') is None and not data.get('description', '').strip():
            raise serializers.ValidationError('Product or description is required')
        return data


class QuoteSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    items = QuoteItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = Quote
        fields = [
            'id', 'number', 'uuid', 'customer', 'customer_name',
            'price_list', 'created_by', 'created_by_name', 'assigned_to',
            'status', 'priority', 'valid_until',
            'description', 'notes',
            'subtotal', 'discount_amount', 'tax_amount', 'total',
            'items', 'items_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['number', 'uuid', 'created_by', 'subtotal', 'tax_amount', 'total', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        # Asegurar valores por defecto
        if 'description' not in validated_data:
            validated_data['description'] = ''
        return super().create(validated_data)


class QuoteDetailSerializer(QuoteSerializer):
    customer = CustomerSerializer(read_only=True)
    
    class Meta(QuoteSerializer.Meta):
        pass


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'description', 'width_mm', 'height_mm',
            'quantity', 'unit_price', 'discount_pct', 'tax_rate',
            'subtotal', 'discount_amount', 'tax_amount', 'total',
            'line_number', 'production_status'
        ]
        read_only_fields = ['subtotal', 'discount_amount', 'tax_amount', 'total']


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    quote_number = serializers.CharField(source='quote.number', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'number', 'uuid', 'customer', 'customer_name',
            'quote', 'quote_number', 'price_list',
            'created_by', 'created_by_name', 'assigned_to',
            'type', 'status', 'payment_status',
            'order_date', 'delivery_date', 'delivered_at',
            'title', 'description', 'notes',
            'subtotal', 'discount_amount', 'tax_amount', 'total',
            'items', 'items_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['number', 'uuid', 'order_date', 'subtotal', 'tax_amount', 'total', 'created_at', 'updated_at']


class OrderDetailSerializer(OrderSerializer):
    customer = CustomerSerializer(read_only=True)
    
    class Meta(OrderSerializer.Meta):
        pass