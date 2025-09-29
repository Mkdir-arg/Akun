from rest_framework import serializers
from .models import Cliente, Direccion, Contacto, TerminoPago, EtiquetaCliente, NotaCliente, ArchivoCliente


class EtiquetaClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtiquetaCliente
        fields = ['id', 'name', 'color', 'is_active']


class TerminoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerminoPago
        fields = ['id', 'name', 'days', 'early_discount_pct', 'notes', 'is_active']


class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = ['id', 'customer', 'kind', 'street', 'number', 'city', 'province', 
                 'postal_code', 'country', 'is_default']
        
    def validate(self, data):
        if data.get('is_default'):
            customer = data.get('customer')
            kind = data.get('kind')
            
            existing = Direccion.objects.filter(
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


class ContactoSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Contacto
        fields = ['id', 'customer', 'first_name', 'last_name', 'full_name', 
                 'email', 'phone', 'role', 'is_primary']
        
    def validate(self, data):
        if data.get('is_primary'):
            customer = data.get('customer')
            
            existing = Contacto.objects.filter(
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


class NotaClienteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = NotaCliente
        fields = ['id', 'customer', 'author', 'author_name', 'body', 'pinned', 
                 'created_at', 'updated_at']
        read_only_fields = ['author']


class ArchivoClienteSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = ArchivoCliente
        fields = ['id', 'customer', 'file', 'title', 'uploaded_by', 'uploaded_by_name',
                 'uploaded_at', 'file_size']
        read_only_fields = ['uploaded_by']
        
    def get_file_size(self, obj):
        try:
            return obj.file.size
        except:
            return 0


class ClienteSerializer(serializers.ModelSerializer):
    etiqueta_name = serializers.CharField(source='etiqueta.name', read_only=True)
    direccion_completa = serializers.ReadOnlyField()
    
    class Meta:
        model = Cliente
        fields = ['id', 'code', 'type', 'name', 'tax_id', 'email', 'phone',
                 'provincia', 'localidad', 'municipio', 'calle', 'numero', 'codigo_postal',
                 'direccion_completa', 'status', 'etiqueta', 'etiqueta_name',
                 'notes', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['code']


class ClienteDetailSerializer(ClienteSerializer):
    addresses = DireccionSerializer(many=True, read_only=True)
    contacts = ContactoSerializer(many=True, read_only=True)
    customer_notes = NotaClienteSerializer(many=True, read_only=True)
    files = ArchivoClienteSerializer(many=True, read_only=True)
    
    class Meta(ClienteSerializer.Meta):
        fields = ClienteSerializer.Meta.fields + ['addresses', 'contacts', 'customer_notes', 'files']