from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# app_name = 'catalog'  # Removido para evitar conflicto

router = DefaultRouter()
router.register(r'products', views.ProductoViewSet)
router.register(r'categories', views.CategoriaProductoViewSet)
router.register(r'uoms', views.UnidadMedidaViewSet)
router.register(r'tax-rates', views.TasaImpuestoViewSet)
router.register(r'price-lists', views.ListaPreciosViewSet)
router.register(r'price-rules', views.ReglaListaPreciosViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]