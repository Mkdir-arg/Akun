from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Role

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            try:
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
                if not user:
                    raise serializers.ValidationError('Credenciales inválidas')
                if not user.is_active:
                    raise serializers.ValidationError('Usuario inactivo')
                attrs['user'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError('Credenciales inválidas')
        else:
            raise serializers.ValidationError('Email y contraseña requeridos')
        
        return attrs


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'can_access_crm', 'can_access_catalog',
            'can_access_orders', 'can_access_quotes', 'can_access_reports',
            'can_access_settings', 'can_create', 'can_edit', 'can_delete',
            'can_export', 'is_active', 'created_at', 'updated_at'
        ]


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'role_name', 'is_active', 'is_staff', 'is_superuser', 'password',
            'created_at', 'updated_at', 'last_login'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    role_permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'is_superuser', 'role_permissions'
        ]
    
    def get_role_permissions(self, obj):
        if obj.is_superuser:
            return {
                'can_access_crm': True,
                'can_access_catalog': True,
                'can_access_orders': True,
                'can_access_quotes': True,
                'can_access_reports': True,
                'can_access_settings': True,
                'can_create': True,
                'can_edit': True,
                'can_delete': True,
                'can_export': True,
            }
        
        if not obj.role:
            return {}
        
        return {
            'can_access_crm': obj.role.can_access_crm,
            'can_access_catalog': obj.role.can_access_catalog,
            'can_access_orders': obj.role.can_access_orders,
            'can_access_quotes': obj.role.can_access_quotes,
            'can_access_reports': obj.role.can_access_reports,
            'can_access_settings': obj.role.can_access_settings,
            'can_create': obj.role.can_create,
            'can_edit': obj.role.can_edit,
            'can_delete': obj.role.can_delete,
            'can_export': obj.role.can_export,
        }