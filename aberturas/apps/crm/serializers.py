from rest_framework import serializers
from .models import Customer, Address, Contact, PaymentTerm, CustomerTag, CustomerNote, CustomerFile


class CustomerTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTag
        fields = ['id', 'name', 'color', 'is_active']


class PaymentTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTerm
        fields = ['id', 'name', 'days', 'early_discount_pct', 'notes', 'is_active']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'customer', 'kind', 'street', 'number', 'city', 'province', 
                 'postal_code', 'country', 'is_default']
        
    def validate(self, data):
        if data.get('is_default'):
            customer = data.get('customer')
            kind = data.get('kind')
            
            existing = Address.objects.filter(
                customer=customer,
                kind=kind,
                is_default=True
            )
            
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
                
            if existing.exists():
                raise serializers.ValidationError(
                    f'Ya existe una dirección por defecto de tipo {kind} para este cliente.'
                )
        return data


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Contact
        fields = ['id', 'customer', 'first_name', 'last_name', 'full_name', 
                 'email', 'phone', 'role', 'is_primary']
        
    def validate(self, data):
        if data.get('is_primary'):
            customer = data.get('customer')
            
            existing = Contact.objects.filter(
                customer=customer,
                is_primary=True
            )
            
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
                
            if existing.exists():
                raise serializers.ValidationError(
                    'Ya existe un contacto principal para este cliente.'
                )
        return data


class CustomerNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = CustomerNote
        fields = ['id', 'customer', 'author', 'author_name', 'body', 'pinned', 
                 'created_at', 'updated_at']
        read_only_fields = ['author']


class CustomerFileSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerFile
        fields = ['id', 'customer', 'file', 'title', 'uploaded_by', 'uploaded_by_name',
                 'uploaded_at', 'file_size']
        read_only_fields = ['uploaded_by']
        
    def get_file_size(self, obj):
        try:
            return obj.file.size
        except:
            return 0


class CustomerSerializer(serializers.ModelSerializer):
    tags = CustomerTagSerializer(many=True, read_only=True)
    default_price_list_name = serializers.CharField(source='default_price_list.name', read_only=True)
    payment_terms_name = serializers.CharField(source='payment_terms.name', read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'code', 'type', 'name', 'tax_id', 'email', 'phone',
                 'default_price_list', 'default_price_list_name', 'payment_terms', 
                 'payment_terms_name', 'credit_limit', 'status', 'tags', 'notes',
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['code']
        
    def validate_credit_limit(self, value):
        if value < 0:
            raise serializers.ValidationError('El límite de crédito no puede ser negativo.')
        return value


class CustomerDetailSerializer(CustomerSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    contacts = ContactSerializer(many=True, read_only=True)
    customer_notes = CustomerNoteSerializer(many=True, read_only=True)
    files = CustomerFileSerializer(many=True, read_only=True)
    
    class Meta(CustomerSerializer.Meta):
        fields = CustomerSerializer.Meta.fields + ['addresses', 'contacts', 'customer_notes', 'files']