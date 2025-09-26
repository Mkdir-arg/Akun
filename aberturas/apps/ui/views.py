from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from apps.accounts.serializers import LoginSerializer, UserSerializer


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'ui/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_users': 0,  # Placeholder
            'total_orders': 0,  # Placeholder
            'total_products': 0,  # Placeholder
        })
        return context


class AboutView(TemplateView):
    template_name = 'ui/about.html'


def health_check(request):
    """Vista de health check para monitoreo."""
    return JsonResponse({'status': 'ok'})


@login_required
def htmx_example(request):
    """Ejemplo básico de HTMX con filtro."""
    query = request.GET.get('q', '')
    
    # Datos de ejemplo
    items = [
        {'id': 1, 'name': 'Ventana Corrediza'},
        {'id': 2, 'name': 'Puerta Principal'},
        {'id': 3, 'name': 'Ventana Batiente'},
        {'id': 4, 'name': 'Puerta Balcón'},
    ]
    
    if query:
        items = [item for item in items if query.lower() in item['name'].lower()]
    
    if request.htmx:
        return render(request, 'ui/partials/items_list.html', {'items': items})
    
    return render(request, 'ui/htmx_example.html', {'items': items})

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Login exitoso'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout exitoso'})

class DashboardAPIView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'user': UserSerializer(request.user).data,
            'stats': {
                'total_users': 25,
                'total_orders': 142,
                'total_products': 89,
                'revenue': 45600
            }
        })