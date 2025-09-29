from django import forms
from .models import Cliente, Direccion


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'type', 'name', 'tax_id', 'email', 'phone', 
            'default_price_list', 'credit_limit', 'notes', 'is_active'
        ]
        widgets = {
            'type': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'tax_id': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'email': forms.EmailInput(attrs={'class': 'input input-bordered w-full'}),
            'phone': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'default_price_list': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }


class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = [
            'kind', 'street', 'number', 'city', 'province', 
            'postal_code', 'country', 'is_default'
        ]
        widgets = {
            'kind': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'street': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'number': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'city': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'province': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'postal_code': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'country': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }