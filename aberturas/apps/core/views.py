from rest_framework import viewsets
from .models import Moneda
from .serializers import MonedaSerializer


class MonedaViewSet(viewsets.ModelViewSet):
    queryset = Moneda.objects.filter(is_active=True)
    serializer_class = MonedaSerializer