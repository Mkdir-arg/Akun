import django_filters
from .models import Customer, Address, Contact


class CustomerFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Customer.STATUS_CHOICES)
    is_active = django_filters.BooleanFilter()
    type = django_filters.ChoiceFilter(choices=Customer.TYPE_CHOICES)
    default_price_list = django_filters.NumberFilter()
    tag = django_filters.NumberFilter(field_name='tags__id')
    created_at_from = django_filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    created_at_to = django_filters.DateFilter(field_name='created_at__date', lookup_expr='lte')
    
    class Meta:
        model = Customer
        fields = ['status', 'is_active', 'type', 'default_price_list', 'tag']


class AddressFilter(django_filters.FilterSet):
    customer = django_filters.NumberFilter()
    kind = django_filters.ChoiceFilter(choices=Address.KIND_CHOICES)
    
    class Meta:
        model = Address
        fields = ['customer', 'kind']


class ContactFilter(django_filters.FilterSet):
    customer = django_filters.NumberFilter()
    is_primary = django_filters.BooleanFilter()
    
    class Meta:
        model = Contact
        fields = ['customer', 'is_primary']