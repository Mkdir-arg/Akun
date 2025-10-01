from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Presupuestos
    path('presupuestos/', views.presupuesto_list, name='presupuesto_list'),
    path('presupuestos/crear/', views.presupuesto_create, name='presupuesto_create'),
    path('presupuestos/<int:pk>/', views.presupuesto_detail, name='presupuesto_detail'),
    path('presupuestos/<int:pk>/agregar-item/', views.presupuesto_add_item, name='presupuesto_add_item'),
    
    # APIs
    path('api/templates/', views.get_templates, name='get_templates'),
    path('api/add-template-item/', views.add_template_item, name='add_template_item'),
    path('api/calculate-template-price/', views.calculate_template_price, name='calculate_template_price'),
]