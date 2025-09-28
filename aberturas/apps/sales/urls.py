from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuoteViewSet, QuoteItemViewSet, OrderViewSet, OrderItemViewSet

router = DefaultRouter()
router.register(r'quotes', QuoteViewSet)
router.register(r'quote-items', QuoteItemViewSet, basename='quoteitem')
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet, basename='orderitem')

urlpatterns = [
    path('api/', include(router.urls)),
]