from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .services.template_filter_service import TemplateFilterService
import json

@require_http_methods(["GET"])
def get_template_categories(request):
    """Lista de categorias dinamicas basadas en extrusoras"""
    categories = TemplateFilterService.get_categories()
    return JsonResponse({"categories": categories})


@require_http_methods(["GET"])
def get_lineas(request):
    """API para obtener lineas disponibles"""
    category_id = request.GET.get("category_id")
    extrusora_id = request.GET.get("extrusora_id")
    try:
        category_id_int = int(category_id) if category_id is not None else None
    except (TypeError, ValueError):
        return JsonResponse({"error": "category_id invalido"}, status=400)
    try:
        extrusora_id_int = int(extrusora_id) if extrusora_id is not None else None
    except (TypeError, ValueError):
        return JsonResponse({"error": "extrusora_id invalido"}, status=400)
    lineas = TemplateFilterService.get_lineas(category_id=category_id_int, extrusora_id=extrusora_id_int)
    return JsonResponse({"lineas": lineas})

@require_http_methods(["GET"])
def get_marcos(request):
    """API para obtener marcos por linea"""
    linea = request.GET.get("linea")
    if not linea:
        return JsonResponse({"error": "Linea requerida"}, status=400)

    marcos = TemplateFilterService.get_marcos(linea)
    return JsonResponse({"marcos": marcos})


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
        
        # Usar el mÃƒÂ©todo existente de AttributeOption
        from .models import AttributeOption
        result = AttributeOption.calculate_pricing(template_id, selections)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_associated_products(request, template_id):
    """API para obtener productos especÃƒÂ­ficamente asociados a una plantilla"""
    try:
        from .models import ProductTemplate
        
        # Obtener la plantilla principal
        main_template = ProductTemplate.objects.get(id=template_id)
        
        # LÃƒÂ³gica de productos asociados basada en reglas de negocio
        associated = []
        
        # 1. Accesorios de la misma lÃƒÂ­nea
        accessories = ProductTemplate.objects.filter(
            line_name=main_template.line_name,
            product_class='ACCESORIO',
            is_active=True
        ).exclude(id=template_id)
        
        for acc in accessories:
            associated.append({
                'id': acc.id,
                'product_class': acc.product_class,
                'line_name': acc.line_name,
                'code': acc.code,
                'base_price_net': float(acc.base_price_net),
                'currency': acc.currency,
                'relationship_type': 'ACCESORIO_LINEA'
            })
        
        # 2. Productos complementarios (ej: mosquiteros para ventanas)
        if main_template.product_class == 'VENTANA':
            mosquiteros = ProductTemplate.objects.filter(
                line_name=main_template.line_name,
                code__icontains='MOSQUITERO',
                is_active=True
            ).exclude(id=template_id)
            
            for mosq in mosquiteros:
                associated.append({
                    'id': mosq.id,
                    'product_class': mosq.product_class,
                    'line_name': mosq.line_name,
                    'code': mosq.code,
                    'base_price_net': float(mosq.base_price_net),
                    'currency': mosq.currency,
                    'relationship_type': 'COMPLEMENTARIO'
                })
        
        return JsonResponse({
            'main_product': {
                'id': main_template.id,
                'product_class': main_template.product_class,
                'line_name': main_template.line_name,
                'code': main_template.code
            },
            'associated_products': associated
        })
        
    except ProductTemplate.DoesNotExist:
        return JsonResponse({'error': 'Plantilla no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
