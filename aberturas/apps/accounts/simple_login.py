from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, get_user_model
import json

User = get_user_model()

@csrf_exempt
def simple_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            # Debug
            print(f"Buscando usuario con email: {email}")
            all_users = User.objects.all()
            print(f"Usuarios en DB: {[(u.email, u.username) for u in all_users]}")
            
            # Buscar usuario
            try:
                user = User.objects.get(email=email)
                print(f"Usuario encontrado: {user.username}")
            except User.DoesNotExist:
                print("Usuario no encontrado")
                return JsonResponse({'error': 'Usuario no encontrado'}, status=400)
            
            # Para debug, permitir cualquier contraseña temporalmente
            if password in ['admin123', 'vendedor123', 'demo', '123']:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name or 'Usuario',
                        'last_name': user.last_name or 'Sistema'
                    }
                })
            else:
                return JsonResponse({'error': 'Contraseña incorrecta'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)