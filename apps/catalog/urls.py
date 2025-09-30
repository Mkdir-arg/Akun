from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.ProductTemplateViewSet)
router.register(r'attributes', views.TemplateAttributeViewSet)
router.register(r'options', views.AttributeOptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]