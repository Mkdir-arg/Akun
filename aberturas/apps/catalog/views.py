from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Product, ProductCategory, UoM, TaxRate, PriceList, PriceListRule
from .serializers import (
    ProductSerializer, ProductDetailSerializer, ProductCategorySerializer,
    UoMSerializer, TaxRateSerializer, PriceListSerializer, PriceListRuleSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category', 'uom', 'tax').prefetch_related('pricelistrule_set')
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['sku', 'name', 'material', 'opening_type']
    ordering_fields = ['sku', 'name', 'base_price', 'price_per_m2']
    ordering = ['sku']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        material = self.request.query_params.get('material')
        if material:
            queryset = queryset.filter(material=material)
            
        opening_type = self.request.query_params.get('opening_type')
        if opening_type:
            queryset = queryset.filter(opening_type=opening_type)
            
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        pricing_method = self.request.query_params.get('pricing_method')
        if pricing_method:
            queryset = queryset.filter(pricing_method=pricing_method)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        product = self.get_object()
        product.is_active = True
        product.save()
        return Response({'status': 'Producto activado'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        product = self.get_object()
        product.is_active = False
        product.save()
        return Response({'status': 'Producto desactivado'})
    
    @action(detail=True, methods=['post'])
    def calculate_price(self, request, pk=None):
        product = self.get_object()
        width_mm = request.data.get('width_mm')
        height_mm = request.data.get('height_mm')
        price_list_id = request.data.get('price_list_id')
        
        try:
            if price_list_id:
                price_rule = PriceListRule.objects.get(
                    product=product,
                    price_list_id=price_list_id
                )
                unit_price = price_rule.compute_unit_price(width_mm, height_mm)
            else:
                # Usar precios base del producto
                if product.pricing_method == 'FIXED':
                    unit_price = product.base_price
                else:
                    if width_mm and height_mm:
                        area = (float(width_mm) / 1000) * (float(height_mm) / 1000)
                        area = max(area, float(product.min_area_m2))
                        unit_price = float(product.price_per_m2) * area
                    else:
                        unit_price = float(product.price_per_m2)
                        
            return Response({
                'unit_price': round(unit_price, 2),
                'pricing_method': product.pricing_method,
                'area_m2': (float(width_mm) / 1000) * (float(height_mm) / 1000) if width_mm and height_mm else None
            })
            
        except PriceListRule.DoesNotExist:
            return Response(
                {'error': 'No se encontró regla de precio para esta lista'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.select_related('parent').filter(is_active=True)
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]
    ordering = ['name']


class UoMViewSet(viewsets.ModelViewSet):
    queryset = UoM.objects.filter(is_active=True)
    serializer_class = UoMSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['name']


class TaxRateViewSet(viewsets.ModelViewSet):
    queryset = TaxRate.objects.all()
    serializer_class = TaxRateSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['name']


class PriceListViewSet(viewsets.ModelViewSet):
    queryset = PriceList.objects.all()
    serializer_class = PriceListSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['name']


class PriceListRuleViewSet(viewsets.ModelViewSet):
    queryset = PriceListRule.objects.select_related('price_list', 'product')
    serializer_class = PriceListRuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        price_list = self.request.query_params.get('price_list')
        if price_list:
            queryset = queryset.filter(price_list=price_list)
            
        product = self.request.query_params.get('product')
        if product:
            queryset = queryset.filter(product=product)
            
        return queryset