from django.contrib import admin
from .models import Customer, Address


class AddressInline(admin.TabularInline):
    model = Address
    extra = 1
    fields = ('kind', 'street', 'number', 'city', 'province', 'postal_code', 'is_default')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'type', 'tax_id', 'email', 'phone', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('code', 'name', 'tax_id', 'email')
    list_select_related = ('default_price_list',)
    inlines = [AddressInline]
    readonly_fields = ('code',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('code', 'type', 'name', 'tax_id', 'is_active')
        }),
        ('Contacto', {
            'fields': ('email', 'phone')
        }),
        ('Comercial', {
            'fields': ('default_price_list', 'credit_limit')
        }),
        ('Notas', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'kind', 'street', 'number', 'city', 'province', 'is_default')
    list_filter = ('kind', 'province', 'is_default')
    search_fields = ('customer__name', 'street', 'city')
    list_select_related = ('customer',)