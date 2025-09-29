from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Producto, CategoriaProducto, UnidadMedida, TasaImpuesto, ListaPrecios, ReglaListaPrecios
from .serializers import (
    ProductoSerializer, ProductoDetailSerializer, CategoriaProductoSerializer,
    UnidadMedidaSerializer, TasaImpuestoSerializer, ListaPreciosSerializer, ReglaListaPreciosSerializer
)


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.select_related('category', 'uom', 'tax')
    permission_classes = []  # Temporalmente sin permisos
    
    def create(self, request, *args, **kwargs):
        # Si no hay SKU, generar uno automáticamente
        if not request.data.get('sku'):
            category_id = request.data.get('category')
            if category_id:
                try:
                    category = CategoriaProducto.objects.get(id=category_id)
                    prefix = category.code.upper()[:3]
                    last_product = Producto.objects.filter(sku__startswith=prefix).order_by('-id').first()
                    
                    if last_product:
                        try:
                            last_number = int(last_product.sku.split('-')[-1])
                            new_number = last_number + 1
                        except (ValueError, IndexError):
                            new_number = 1
                    else:
                        new_number = 1
                    
                    request.data['sku'] = f"{prefix}-{new_number:03d}"
                except CategoriaProducto.DoesNotExist:
                    pass
        
        return super().create(request, *args, **kwargs)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['sku', 'name', 'material', 'opening_type']
    ordering_fields = ['sku', 'name', 'base_price', 'price_per_m2']
    ordering = ['sku']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductoDetailSerializer
        return ProductoSerializer
    
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
    
    @action(detail=False, methods=['post'])
    def generate_sku(self, request):
        category_id = request.data.get('category_id')
        if not category_id:
            return Response({'error': 'category_id requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = CategoriaProducto.objects.get(id=category_id)
            prefix = category.code.upper()[:3]
            last_product = Producto.objects.filter(sku__startswith=prefix).order_by('-id').first()
            
            if last_product:
                try:
                    last_number = int(last_product.sku.split('-')[-1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            
            new_sku = f"{prefix}-{new_number:03d}"
            return Response({'sku': new_sku})
            
        except CategoriaProducto.DoesNotExist:
            return Response({'error': 'Categoría no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def calculate_price(self, request, pk=None):
        product = self.get_object()
        width_mm = request.data.get('width_mm')
        height_mm = request.data.get('height_mm')
        price_list_id = request.data.get('price_list_id')
        
        try:
            if price_list_id:
                price_rule = ReglaListaPrecios.objects.get(
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
            
        except ReglaListaPrecios.DoesNotExist:
            return Response(
                {'error': 'No se encontró regla de precio para esta lista'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.select_related('parent').filter(is_active=True)
    serializer_class = CategoriaProductoSerializer
    permission_classes = []  # Temporalmente sin permisos
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        category = self.get_object()
        subcategories = Producto.SUBCATEGORY_CHOICES.get(category.code, [])
        return Response({
            'subcategories': [{'value': key, 'label': value} for key, value in subcategories]
        })


class UnidadMedidaViewSet(viewsets.ModelViewSet):
    queryset = UnidadMedida.objects.filter(is_active=True)
    serializer_class = UnidadMedidaSerializer
    permission_classes = []  # Temporalmente sin permisos
    ordering = ['name']


class TasaImpuestoViewSet(viewsets.ModelViewSet):
    queryset = TasaImpuesto.objects.all()
    serializer_class = TasaImpuestoSerializer
    permission_classes = []  # Temporalmente sin permisos
    ordering = ['name']


class ListaPreciosViewSet(viewsets.ModelViewSet):
    queryset = ListaPrecios.objects.all()
    serializer_class = ListaPreciosSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['name']


class ReglaListaPreciosViewSet(viewsets.ModelViewSet):
    queryset = ReglaListaPrecios.objects.select_related('price_list', 'product')
    serializer_class = ReglaListaPreciosSerializer
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