from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('api/provincias/', views.provincias_list, name='provincias_list'),
    path('api/municipios/', views.municipios_list, name='municipios_list'),
    path('api/localidades/', views.localidades_list, name='localidades_list'),
]