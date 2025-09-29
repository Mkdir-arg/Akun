from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PresupuestoViewSet, LineaPresupuestoViewSet, PedidoViewSet, LineaPedidoViewSet

router = DefaultRouter()
router.register(r'quotes', PresupuestoViewSet)
router.register(r'quote-items', LineaPresupuestoViewSet, basename='quoteitem')
router.register(r'orders', PedidoViewSet)
router.register(r'order-items', LineaPedidoViewSet, basename='orderitem')

urlpatterns = [
    path('api/', include(router.urls)),
]