from django.contrib import admin
from django.db import transaction
from .models import (
    UnidadMedida, CategoriaProducto, TasaImpuesto, Producto, ListaPrecios, ReglaListaPrecios,
    MedidaProducto, ColorProducto, LineaProducto
)


@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('code', 'name')
    ordering = ('code',)


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'parent', 'is_active')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'code')
    prepopulated_fields = {'code': ('name',)}


@admin.register(TasaImpuesto)
class TasaImpuestoAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('name',)
    
    def make_default(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Seleccione exactamente una tasa de impuesto.", level='error')
            return
            
        with transaction.atomic():
            TasaImpuesto.objects.filter(is_default=True).update(is_default=False)
            queryset.update(is_default=True)
            
        self.message_user(request, "Tasa de impuesto marcada como predeterminada.")
    
    make_default.short_description = "Marcar como predeterminada"
    actions = [make_default]


@admin.register(MedidaProducto)
class MedidaProductoAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(ColorProducto)
class ColorProductoAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'hex_color', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(LineaProducto)
class LineaProductoAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'medida', 'color', 'linea', 'category', 'material', 'opening_type', 'pricing_method', 'is_active')
    list_filter = ('category', 'material', 'opening_type', 'pricing_method', 'is_active', 'is_service', 'medida', 'color', 'linea')
    search_fields = ('sku', 'medida__name', 'color__name', 'linea__name')
    list_select_related = ('category', 'tax', 'medida', 'color', 'linea')
    fieldsets = (
        ('Información Básica', {
            'fields': ('sku', 'category', 'is_service', 'is_active')
        }),
        ('Especificaciones', {
            'fields': ('medida', 'color', 'linea', 'material', 'opening_type', 'glass_type')
        }),
        ('Dimensiones y Peso', {
            'fields': ('width_mm', 'height_mm', 'weight_kg')
        }),
        ('Precios e Impuestos', {
            'fields': ('tax', 'pricing_method', 'base_price', 'price_per_m2', 'min_area_m2')
        }),
    )


@admin.register(ListaPrecios)
class ListaPreciosAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency', 'is_default', 'active_from', 'active_to')
    list_filter = ('currency', 'is_default')
    search_fields = ('name',)
    
    def make_default(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Seleccione exactamente una lista de precios.", level='error')
            return
            
        with transaction.atomic():
            ListaPrecios.objects.filter(is_default=True).update(is_default=False)
            queryset.update(is_default=True)
            
        self.message_user(request, "Lista de precios marcada como predeterminada.")
    
    make_default.short_description = "Marcar como predeterminada"
    actions = [make_default]


@admin.register(ReglaListaPrecios)
class ReglaListaPreciosAdmin(admin.ModelAdmin):
    list_display = ('price_list', 'product', 'method', 'discount_pct', 'valid_from', 'valid_to')
    list_filter = ('method', 'price_list')
    search_fields = ('product__sku', 'price_list__name')
    list_select_related = ('product', 'price_list')
    autocomplete_fields = ('product',)