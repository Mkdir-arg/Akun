from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MonedaViewSet

router = DefaultRouter()
router.register(r'currencies', MonedaViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]