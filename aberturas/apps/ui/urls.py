from django.urls import path
from .views import DashboardView, AboutView, health_check, htmx_example

app_name = 'ui'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('about/', AboutView.as_view(), name='about'),
    path('health/', health_check, name='health'),
    path('htmx-example/', htmx_example, name='htmx_example'),
]