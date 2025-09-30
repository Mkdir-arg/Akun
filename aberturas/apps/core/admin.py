from django.contrib import admin
from .models import Moneda, Provincia, Municipio, Localidad


@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'exchange_rate', 'is_default', 'is_active']
    list_filter = ['is_default', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']
    ordering = ['nombre']


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'provincia']
    list_filter = ['provincia']
    search_fields = ['nombre', 'provincia__nombre']
    ordering = ['provincia__nombre', 'nombre']


@admin.register(Localidad)
class LocalidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'municipio', 'get_provincia']
    list_filter = ['municipio__provincia']
    search_fields = ['nombre', 'municipio__nombre', 'municipio__provincia__nombre']
    ordering = ['municipio__provincia__nombre', 'municipio__nombre', 'nombre']

    def get_provincia(self, obj):
        return obj.municipio.provincia.nombre
    get_provincia.short_description = 'Provincia'