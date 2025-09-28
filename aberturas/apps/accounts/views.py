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
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import RoleBasedPermission, AdminOnlyPermission
from .models import Role
from .serializers import RoleSerializer, UserSerializer, UserProfileSerializer
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
        print(f"DEBUG: Request body: {request.body}")
        print(f"DEBUG: Content type: {request.content_type}")
        
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = {
                    'email': request.POST.get('email'),
                    'password': request.POST.get('password')
                }
            
            email = data.get('email')
            password = data.get('password')
            
            print(f"DEBUG: Email: {email}, Password: {'*' * len(password) if password else None}")
            
            if not email or not password:
                return JsonResponse({'error': 'Email y contraseña requeridos'}, status=400)
            
            # Buscar usuario por email
            try:
                user = User.objects.get(email=email)
                print(f"DEBUG: Usuario encontrado: {user.username}, activo: {user.is_active}")
            except User.DoesNotExist:
                print("DEBUG: Usuario no encontrado")
                return JsonResponse({'error': 'Credenciales inválidas'}, status=400)
            
            # Autenticar
            user_auth = authenticate(request, username=user.username, password=password)
            print(f"DEBUG: Resultado autenticación: {user_auth}")
            
            if user_auth and user_auth.is_active:
                login(request, user_auth)
                print("DEBUG: Login exitoso")
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
                print("DEBUG: Autenticación falló")
                return JsonResponse({'error': 'Credenciales inválidas'}, status=400)
                
        except json.JSONDecodeError:
            print("DEBUG: Error decodificando JSON")
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            print(f"DEBUG: Error inesperado: {str(e)}")
            return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)


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


@method_decorator(csrf_exempt, name='dispatch')
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = []  # Temporalmente sin permisos
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        role = self.get_object()
        role.is_active = True
        role.save()
        return Response({'status': 'Rol activado'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        role = self.get_object()
        role.is_active = False
        role.save()
        return Response({'status': 'Rol desactivado'})


@method_decorator(csrf_exempt, name='dispatch')
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('role')
    serializer_class = UserSerializer
    permission_classes = []  # Temporalmente sin permisos
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'first_name', 'last_name', 'created_at']
    ordering = ['first_name', 'last_name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'Usuario activado'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'Usuario desactivado'})
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        new_password = request.data.get('password')
        if new_password:
            user.set_password(new_password)
            user.save()
            return Response({'status': 'Contraseña actualizada'})
        return Response({'error': 'Contraseña requerida'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_profile(request):
    if request.user.is_authenticated:
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)