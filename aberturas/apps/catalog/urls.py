from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# app_name = 'catalog'  # Removido para evitar conflicto

router = DefaultRouter()
router.register(r'categories', views.CategoriaProductoViewSet)
router.register(r'subcategories', views.SubcategoriaProductoViewSet)
router.register(r'products', views.ProductoViewSet)
router.register(r'medidas', views.MedidaProductoViewSet)
router.register(r'colores', views.ColorProductoViewSet)
router.register(r'lineas', views.LineaProductoViewSet)
router.register(r'tax-rates', views.TasaImpuestoViewSet)
router.register(r'currencies', views.MonedaViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]