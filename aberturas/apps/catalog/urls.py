from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'catalog'

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.ProductCategoryViewSet)
router.register(r'uoms', views.UoMViewSet)
router.register(r'tax-rates', views.TaxRateViewSet)
router.register(r'price-lists', views.PriceListViewSet)
router.register(r'price-rules', views.PriceListRuleViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]