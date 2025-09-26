from django import forms
from .models import Product, PriceList, PriceListRule


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'sku', 'name', 'category', 'uom', 'material', 'opening_type', 
            'glass_type', 'color_code', 'width_mm', 'height_mm', 'weight_kg',
            'tax', 'pricing_method', 'base_price', 'price_per_m2', 'min_area_m2',
            'is_service', 'is_active'
        ]
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'category': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'uom': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'material': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'opening_type': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'glass_type': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'color_code': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'width_mm': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'height_mm': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.001'}),
            'tax': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'pricing_method': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'base_price': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
            'price_per_m2': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
            'min_area_m2': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
            'is_service': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }


class PriceListForm(forms.ModelForm):
    class Meta:
        model = PriceList
        fields = ['name', 'currency', 'is_default', 'active_from', 'active_to']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'currency': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'active_from': forms.DateInput(attrs={'class': 'input input-bordered w-full', 'type': 'date'}),
            'active_to': forms.DateInput(attrs={'class': 'input input-bordered w-full', 'type': 'date'}),
        }


class PriceListRuleForm(forms.ModelForm):
    class Meta:
        model = PriceListRule
        fields = [
            'product', 'method', 'fixed_price', 'price_per_m2', 'min_area_m2',
            'discount_pct', 'valid_from', 'valid_to'
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'method': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'fixed_price': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
            'price_per_m2': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
            'min_area_m2': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
            'discount_pct': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
            'valid_from': forms.DateInput(attrs={'class': 'input input-bordered w-full', 'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'class': 'input input-bordered w-full', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        pricelist_pk = kwargs.pop('pricelist_pk', None)
        super().__init__(*args, **kwargs)
        
        if pricelist_pk:
            # Filtrar productos que no tengan regla en esta lista
            existing_rules = PriceListRule.objects.filter(price_list_id=pricelist_pk)
            if self.instance.pk:
                existing_rules = existing_rules.exclude(pk=self.instance.pk)
            
            excluded_products = existing_rules.values_list('product_id', flat=True)
            self.fields['product'].queryset = Product.objects.exclude(
                id__in=excluded_products
            ).filter(is_active=True)