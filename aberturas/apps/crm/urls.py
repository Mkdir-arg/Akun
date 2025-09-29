from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'crm'

router = DefaultRouter()
router.register(r'customers', views.ClienteViewSet)
router.register(r'addresses', views.DireccionViewSet, basename='address')
router.register(r'contacts', views.ContactoViewSet, basename='contact')
router.register(r'payment-terms', views.TerminoPagoViewSet)
router.register(r'customer-tags', views.EtiquetaClienteViewSet)
router.register(r'notes', views.NotaClienteViewSet, basename='customernote')
router.register(r'files', views.ArchivoClienteViewSet, basename='customerfile')

urlpatterns = [
    path('api/', include(router.urls)),
]