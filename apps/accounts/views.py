from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
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

class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True
    success_url = '/admin/'

@method_decorator(csrf_exempt, name='dispatch')
class APILoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return JsonResponse({'error': 'Email y contraseña requeridos'}, status=400)
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Credenciales inválidas'}, status=400)
            
            user_auth = authenticate(request, username=user.username, password=password)
            
            if user_auth and user_auth.is_active:
                login(request, user_auth)
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': user_auth.id,
                        'email': user_auth.email,
                        'first_name': user_auth.first_name,
                        'last_name': user_auth.last_name
                    }
                })
            else:
                return JsonResponse({'error': 'Credenciales inválidas'}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    
    def post(self, request):
        logout(request)
        return JsonResponse({'success': True})