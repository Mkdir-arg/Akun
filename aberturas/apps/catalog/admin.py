from django.contrib import admin
from .models import ProductTemplate, TemplateAttribute, AttributeOption


# ============ ADMIN PARA PLANTILLAS ============

class AttributeOptionInline(admin.TabularInline):
    model = AttributeOption
    extra = 0
    fields = ('order', 'label', 'code', 'pricing_mode', 'price_value', 'is_default')
    ordering = ('order',)


class TemplateAttributeInline(admin.TabularInline):
    model = TemplateAttribute
    extra = 0
    fields = ('order', 'name', 'code', 'type', 'is_required')
    ordering = ('order',)


@admin.register(ProductTemplate)
class ProductTemplateAdmin(admin.ModelAdmin):
    list_display = ('line_name', 'product_class', 'code', 'version', 'is_active', 'created_at')
    list_filter = ('product_class', 'is_active', 'requires_dimensions')
    search_fields = ('line_name', 'code')
    inlines = [TemplateAttributeInline]
    fieldsets = (
        ('Información Básica', {
            'fields': ('product_class', 'line_name', 'code', 'version')
        }),
        ('Configuración', {
            'fields': ('base_price_net', 'currency', 'requires_dimensions', 'is_active')
        }),
        ('Vigencia', {
            'fields': ('valid_from', 'valid_to'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('version', 'created_at', 'modified_at')


@admin.register(TemplateAttribute)
class TemplateAttributeAdmin(admin.ModelAdmin):
    list_display = ('template', 'name', 'code', 'type', 'is_required', 'order')
    list_filter = ('type', 'is_required', 'template__product_class')
    search_fields = ('name', 'code', 'template__line_name')
    inlines = [AttributeOptionInline]
    list_select_related = ('template',)


@admin.register(AttributeOption)
class AttributeOptionAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'label', 'code', 'pricing_mode', 'price_value', 'is_default', 'order')
    list_filter = ('pricing_mode', 'is_default', 'attribute__type')
    search_fields = ('label', 'code', 'attribute__name')
    list_select_related = ('attribute', 'attribute__template')