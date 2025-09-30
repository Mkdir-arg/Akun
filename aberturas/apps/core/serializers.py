from rest_framework import serializers
from .models import Moneda


class MonedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moneda
        fields = ['id', 'code', 'name', 'symbol', 'exchange_rate', 'is_default', 'is_active']