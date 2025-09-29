import django_filters
from .models import Cliente, Direccion, Contacto


class ClienteFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Cliente.STATUS_CHOICES)
    is_active = django_filters.BooleanFilter()
    type = django_filters.ChoiceFilter(choices=Cliente.TYPE_CHOICES)
    default_price_list = django_filters.NumberFilter()
    tag = django_filters.NumberFilter(field_name='tags__id')
    created_at_from = django_filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    created_at_to = django_filters.DateFilter(field_name='created_at__date', lookup_expr='lte')
    
    class Meta:
        model = Cliente
        fields = ['status', 'is_active', 'type', 'default_price_list', 'tag']


class DireccionFilter(django_filters.FilterSet):
    customer = django_filters.NumberFilter()
    kind = django_filters.ChoiceFilter(choices=Direccion.KIND_CHOICES)
    
    class Meta:
        model = Direccion
        fields = ['customer', 'kind']


class ContactoFilter(django_filters.FilterSet):
    customer = django_filters.NumberFilter()
    is_primary = django_filters.BooleanFilter()
    
    class Meta:
        model = Contacto
        fields = ['customer', 'is_primary']