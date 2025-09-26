from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

User = get_user_model()

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'autofocus': True}))
    
    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if email and password:
            try:
                user = User.objects.get(email=email)
                self.user_cache = authenticate(self.request, username=user.username, password=password)
                if self.user_cache is None:
                    raise ValidationError("Email o contraseña incorrectos.")
                else:
                    self.confirm_login_allowed(self.user_cache)
            except User.DoesNotExist:
                raise ValidationError("Email o contraseña incorrectos.")
        
        return self.cleaned_data

class AkunLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True
    success_url = '/'

    def form_valid(self, form):
        remember = self.request.POST.get("remember_me") in ("on", "true", "1")
        if remember:
            self.request.session.set_expiry(60*60*24*14)
        else:
            self.request.session.set_expiry(0)
        return super().form_valid(form)


@method_decorator(csrf_exempt, name='dispatch')
class APILoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        user = User.objects.get(email=email)
        user_auth = authenticate(request, username=user.username, password=password)
        
        if user_auth:
            login(request, user_auth)
            return JsonResponse({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
        
        return JsonResponse({'email': ['Credenciales inválidas']}, status=400)


class APILogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'success': True})


class APIDashboardView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
            
        stats = {
            'total_users': User.objects.count(),
            'total_orders': 0,
            'total_products': 0,
            'revenue': 0
        }
        
        return Response({'stats': stats})


@method_decorator(csrf_exempt, name='dispatch')
class APITestView(View):
    def get(self, request):
        return JsonResponse({'message': 'API funcionando', 'status': 'ok'})
    
    def post(self, request):
        return JsonResponse({'message': 'POST funcionando', 'data': 'recibido'})