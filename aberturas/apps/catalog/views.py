from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .services.template_filter_service import TemplateFilterService
import json

@require_http_methods(["GET"])
def get_lineas(request):
    """API para obtener líneas disponibles"""
    lineas = TemplateFilterService.get_lineas()
    return JsonResponse({'lineas': lineas})

@require_http_methods(["GET"])
def get_marcos(request):
    """API para obtener marcos por línea"""
    linea = request.GET.get('linea')
    if not linea:
        return JsonResponse({'error': 'Línea requerida'}, status=400)
    
    marcos = TemplateFilterService.get_marcos(linea)
    return JsonResponse({'marcos': marcos})

@require_http_methods(["GET"])
def get_hojas(request):
    """API para obtener hojas por marco"""
    marco_id = request.GET.get('marco_id')
    if not marco_id:
        return JsonResponse({'error': 'Marco ID requerido'}, status=400)
    
    hojas = TemplateFilterService.get_hojas(marco_id)
    return JsonResponse({'hojas': hojas})

@require_http_methods(["GET"])
def get_interiores(request):
    """API para obtener interiores por hoja"""
    hoja_id = request.GET.get('hoja_id')
    if not hoja_id:
        return JsonResponse({'error': 'Hoja ID requerida'}, status=400)
    
    interiores = TemplateFilterService.get_interiores(hoja_id)
    return JsonResponse({'interiores': interiores})

@require_http_methods(["GET"])
def get_opciones_disponibles(request):
    """API para obtener opciones disponibles (contravidrios, mosquiteros, etc.)"""
    hoja_id = request.GET.get('hoja_id')
    interior_id = request.GET.get('interior_id')
    
    opciones = {}
    
    if hoja_id:
        opciones['mosquitero_available'] = TemplateFilterService.has_mosquiteros(hoja_id)
    
    if interior_id:
        opciones['contravidrio_available'] = TemplateFilterService.has_contravidrios(interior_id)
        opciones['vidrio_repartido_available'] = TemplateFilterService.has_vidrios_repartidos(interior_id)
    
    return JsonResponse({'opciones': opciones})

@csrf_exempt
@require_http_methods(["POST"])
def calculate_price(request):
    """API para calcular precio de plantilla"""
    try:
        data = json.loads(request.body)
        template_id = data.get('template_id')
        selections = data.get('selections', {})
        
        if not template_id:
            return JsonResponse({'error': 'Template ID requerido'}, status=400)
        
        # Usar el método existente de AttributeOption
        from .models import AttributeOption
        result = AttributeOption.calculate_pricing(template_id, selections)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)