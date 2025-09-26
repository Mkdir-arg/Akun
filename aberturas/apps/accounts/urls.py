from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import AkunLoginView, APILoginView, APILogoutView, APIDashboardView, APITestView

urlpatterns = [
    path("login/", AkunLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    # API endpoints
    path("api/test/", APITestView.as_view(), name="api_test"),
    path("api/auth/", APILoginView.as_view(), name="api_auth"),
    path("api/login/", APILoginView.as_view(), name="api_login"),
    path("api/logout/", APILogoutView.as_view(), name="api_logout"),
    path("api/dashboard/", APIDashboardView.as_view(), name="api_dashboard"),
]