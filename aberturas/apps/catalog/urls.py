from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# app_name = 'catalog'  # Removido para evitar conflicto

router = DefaultRouter()
# Nuevas rutas para plantillas
router.register(r'templates', views.ProductTemplateViewSet)
router.register(r'attributes', views.TemplateAttributeViewSet, basename='attributes')
router.register(r'options', views.AttributeOptionViewSet, basename='options')

urlpatterns = [
    path('api/v2/', include(router.urls)),
    path('api/', include(router.urls)),  # Alias para compatibilidad
]