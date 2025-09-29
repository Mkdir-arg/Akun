from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# app_name = 'catalog'  # Removido para evitar conflicto

router = DefaultRouter()
router.register(r'categories', views.CategoriaProductoViewSet)
router.register(r'subcategories', views.SubcategoriaProductoViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]