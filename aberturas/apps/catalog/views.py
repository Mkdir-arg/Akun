from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from decimal import Decimal
from .models import Product, PriceList, PriceListRule
from .forms import ProductForm, PriceListForm, PriceListRuleForm


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'uom', 'tax')
        
        # Búsqueda
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(sku__icontains=q) | Q(name__icontains=q)
            )
        
        # Filtros
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
            
        material = self.request.GET.get('material')
        if material:
            queryset = queryset.filter(material=material)
            
        opening_type = self.request.GET.get('opening_type')
        if opening_type:
            queryset = queryset.filter(opening_type=opening_type)
            
        pricing_method = self.request.GET.get('pricing_method')
        if pricing_method:
            queryset = queryset.filter(pricing_method=pricing_method)
            
        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=is_active == 'true')
        
        # Ordenamiento
        order_by = self.request.GET.get('order_by', 'sku')
        direction = self.request.GET.get('direction', 'asc')
        if direction == 'desc':
            order_by = f'-{order_by}'
        queryset = queryset.order_by(order_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import ProductCategory
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        context['materials'] = Product.MATERIAL_CHOICES
        context['opening_types'] = Product.OPENING_TYPE_CHOICES
        context['pricing_methods'] = Product.PRICING_METHOD_CHOICES
        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            return render(self.request, 'catalog/partials/product_table.html', context)
        return super().render_to_response(context, **response_kwargs)


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Producto creado exitosamente.')
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado exitosamente.')
        return super().form_valid(form)


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


class PriceListListView(LoginRequiredMixin, ListView):
    model = PriceList
    template_name = 'catalog/pricelist_list.html'
    context_object_name = 'pricelists'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = PriceList.objects.all()
        
        # Búsqueda
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)
        
        # Filtros
        is_default = self.request.GET.get('is_default')
        if is_default:
            queryset = queryset.filter(is_default=is_default == 'true')
        
        # Ordenamiento
        order_by = self.request.GET.get('order_by', 'name')
        direction = self.request.GET.get('direction', 'asc')
        if direction == 'desc':
            order_by = f'-{order_by}'
        queryset = queryset.order_by(order_by)
        
        return queryset
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            return render(self.request, 'catalog/partials/pricelist_table.html', context)
        return super().render_to_response(context, **response_kwargs)


class PriceListCreateView(LoginRequiredMixin, CreateView):
    model = PriceList
    form_class = PriceListForm
    template_name = 'catalog/pricelist_form.html'
    success_url = reverse_lazy('catalog:pricelist_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Lista de precios creada exitosamente.')
        return super().form_valid(form)


class PriceListUpdateView(LoginRequiredMixin, UpdateView):
    model = PriceList
    form_class = PriceListForm
    template_name = 'catalog/pricelist_form.html'
    success_url = reverse_lazy('catalog:pricelist_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Lista de precios actualizada exitosamente.')
        return super().form_valid(form)


class PriceListDetailView(LoginRequiredMixin, DetailView):
    model = PriceList
    template_name = 'catalog/pricelist_detail.html'
    context_object_name = 'pricelist'


class PriceListRuleListView(LoginRequiredMixin, ListView):
    model = PriceListRule
    template_name = 'catalog/pricelistrule_list.html'
    context_object_name = 'rules'
    paginate_by = 20
    
    def get_queryset(self):
        self.pricelist = get_object_or_404(PriceList, pk=self.kwargs['pricelist_pk'])
        return PriceListRule.objects.filter(price_list=self.pricelist).select_related('product')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pricelist'] = self.pricelist
        return context


class PriceListRuleCreateView(LoginRequiredMixin, CreateView):
    model = PriceListRule
    form_class = PriceListRuleForm
    template_name = 'catalog/pricelistrule_form.html'
    
    def get_success_url(self):
        return reverse_lazy('catalog:pricelist_rules', kwargs={'pricelist_pk': self.kwargs['pricelist_pk']})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['pricelist_pk'] = self.kwargs['pricelist_pk']
        return kwargs
    
    def form_valid(self, form):
        form.instance.price_list_id = self.kwargs['pricelist_pk']
        messages.success(self.request, 'Regla de precio creada exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pricelist'] = get_object_or_404(PriceList, pk=self.kwargs['pricelist_pk'])
        return context


class PriceListRuleUpdateView(LoginRequiredMixin, UpdateView):
    model = PriceListRule
    form_class = PriceListRuleForm
    template_name = 'catalog/pricelistrule_form.html'
    
    def get_success_url(self):
        return reverse_lazy('catalog:pricelist_rules', kwargs={'pricelist_pk': self.object.price_list.pk})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['pricelist_pk'] = self.object.price_list.pk
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Regla de precio actualizada exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pricelist'] = self.object.price_list
        return context


def pricing_preview(request):
    """Endpoint para preview de precios con HTMX"""
    if request.method == 'POST' and request.htmx:
        product_id = request.POST.get('product_id')
        price_list_id = request.POST.get('price_list_id')
        width_mm = request.POST.get('width_mm')
        height_mm = request.POST.get('height_mm')
        
        try:
            product = Product.objects.get(pk=product_id)
            price_list = PriceList.objects.get(pk=price_list_id)
            
            # Buscar regla específica o usar valores del producto
            try:
                rule = PriceListRule.objects.get(price_list=price_list, product=product)
                unit_price = rule.compute_unit_price(
                    width_mm=int(width_mm) if width_mm else None,
                    height_mm=int(height_mm) if height_mm else None
                )
            except PriceListRule.DoesNotExist:
                # Usar valores del producto directamente
                if product.pricing_method == 'FIXED':
                    unit_price = product.base_price
                else:  # AREA
                    if width_mm and height_mm:
                        area = Decimal(str(int(width_mm) / 1000)) * Decimal(str(int(height_mm) / 1000))
                        area = max(area, product.min_area_m2)
                        unit_price = product.price_per_m2 * area
                    else:
                        unit_price = product.price_per_m2 * product.min_area_m2
            
            context = {
                'unit_price': unit_price,
                'product': product,
                'price_list': price_list,
                'width_mm': width_mm,
                'height_mm': height_mm,
            }
            
            return render(request, 'catalog/partials/pricing_preview.html', context)
            
        except (Product.DoesNotExist, PriceList.DoesNotExist, ValueError):
            return render(request, 'catalog/partials/pricing_preview.html', {'error': 'Datos inválidos'})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)