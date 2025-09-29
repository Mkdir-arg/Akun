from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CategoriaProducto, SubcategoriaProducto, Producto
from .serializers import CategoriaProductoSerializer, SubcategoriaProductoSerializer

class CategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.prefetch_related('subcategories')
    serializer_class = CategoriaProductoSerializer
    permission_classes = []
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering = ['name']
    
    @action(detail=False, methods=['post'], url_path='generate-sku')
    def generate_sku(self, request):
        category_id = request.data.get('category_id')
        if not category_id:
            return Response({'error': 'category_id required'}, status=400)
        
        try:
            category = CategoriaProducto.objects.get(id=category_id)
            # Generar SKU basado en categoría
            prefix = category.code.upper()[:3]
            last_product = Producto.objects.filter(category=category).order_by('-id').first()
            if last_product and last_product.sku:
                try:
                    last_number = int(last_product.sku.split('-')[-1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            
            sku = f"{prefix}-{new_number:03d}"
            return Response({'sku': sku})
        except CategoriaProducto.DoesNotExist:
            return Response({'error': 'Category not found'}, status=404)

class SubcategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = SubcategoriaProducto.objects.select_related('category')
    serializer_class = SubcategoriaProductoSerializer
    permission_classes = []
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'category__name']
    ordering = ['category__name', 'name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset