from rest_framework import viewsets
from .models import Currency
from .serializers import CurrencySerializer


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer