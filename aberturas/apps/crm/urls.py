from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'crm'

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'addresses', views.AddressViewSet, basename='address')
router.register(r'contacts', views.ContactViewSet, basename='contact')
router.register(r'payment-terms', views.PaymentTermViewSet)
router.register(r'customer-tags', views.CustomerTagViewSet)
router.register(r'notes', views.CustomerNoteViewSet, basename='customernote')
router.register(r'files', views.CustomerFileViewSet, basename='customerfile')

urlpatterns = [
    path('api/', include(router.urls)),
]