from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.ProductTemplateViewSet)
router.register(r'attributes', views.TemplateAttributeViewSet, basename='attributes')
router.register(r'options', views.AttributeOptionViewSet, basename='options')

urlpatterns = [
    path('api/', include(router.urls)),
]