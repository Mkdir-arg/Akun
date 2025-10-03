from django.urls import path
from . import views, rest_views

app_name = 'catalog'

urlpatterns = [
    path('api/template-categories/', views.get_template_categories, name='get_template_categories'),
    # APIs para filtrado dinamico
    path('api/lineas/', views.get_lineas, name='get_lineas'),
    path('api/marcos/', views.get_marcos, name='get_marcos'),
    path('api/hojas/', views.get_hojas, name='get_hojas'),
    path('api/interiores/', views.get_interiores, name='get_interiores'),
    path('api/opciones/', views.get_opciones_disponibles, name='get_opciones'),
    path('api/calculate/', views.calculate_price, name='calculate_price'),
    path('api/templates/<int:template_id>/associated/', views.get_associated_products, name='get_associated_products'),
    # REST endpoints para plantillas
    path('api/templates/', rest_views.create_template, name='create_template'),
    path('api/templates/<int:template_id>/clone/', rest_views.clone_template, name='clone_template'),
    path('api/templates/<int:template_id>/', rest_views.delete_template, name='delete_template'),
]
