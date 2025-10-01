from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # APIs para filtrado dinámico
    path('api/lineas/', views.get_lineas, name='get_lineas'),
    path('api/marcos/', views.get_marcos, name='get_marcos'),
    path('api/hojas/', views.get_hojas, name='get_hojas'),
    path('api/interiores/', views.get_interiores, name='get_interiores'),
    path('api/opciones/', views.get_opciones_disponibles, name='get_opciones'),
    path('api/calculate/', views.calculate_price, name='calculate_price'),
]