from django.urls import path, include
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter
from .views import AkunLoginView, APILoginView, APILogoutView, APIDashboardView, APITestView, RoleViewSet, UserViewSet, user_profile
from .simple_login import simple_login

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path("login/", AkunLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    # API endpoints
    path("api/test/", APITestView.as_view(), name="api_test"),
    path("api/auth/", APILoginView.as_view(), name="api_auth"),
    path("api/login/", APILoginView.as_view(), name="api_login"),
    path("api/logout/", APILogoutView.as_view(), name="api_logout"),
    path("api/dashboard/", APIDashboardView.as_view(), name="api_dashboard"),
    path("api/profile/", user_profile, name="api_profile"),
    path("api/simple-login/", simple_login, name="simple_login"),
    path('api/', include(router.urls)),
]