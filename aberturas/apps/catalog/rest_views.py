from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from .models import ProductTemplate, TemplateCategory
import json


@csrf_exempt
@require_http_methods(["POST"])
def create_template(request):
    """API para crear nueva plantilla"""
    try:
        data = json.loads(request.body)
        
        line_name = data.get('line_name', '').strip()
        code = data.get('code', '').strip()
        product_class = data.get('product_class', 'VENTANA')
        category_id = data.get('category_id')
        
        if not line_name:
            return JsonResponse({'error': 'line_name requerido'}, status=400)
        
        if not code:
            code = slugify(line_name)
        
        # Verificar que el código sea único
        if ProductTemplate.objects.filter(code=code).exists():
            code = f"{code}-{ProductTemplate.objects.count() + 1}"
        
        template_data = {
            'line_name': line_name,
            'code': code,
            'product_class': product_class,
            'base_price_net': data.get('base_price_net', 0),
            'currency': data.get('currency', 'ARS'),
            'requires_dimensions': data.get('requires_dimensions', True),
            'is_active': data.get('is_active', True),
            'version': data.get('version', 1),
        }
        
        if category_id:
            template_data['category_id'] = category_id
            template_data['legacy_extrusora_id'] = data.get('legacy_extrusora_id')
        
        template = ProductTemplate.objects.create(**template_data)
        
        return JsonResponse({
            'success': True,
            'template': {
                'id': template.id,
                'code': template.code,
                'line_name': template.line_name,
                'product_class': template.product_class,
                'is_active': template.is_active,
                'created_at': template.created_at.isoformat() if template.created_at else None,
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def clone_template(request, template_id):
    """API para duplicar plantilla"""
    try:
        original = get_object_or_404(ProductTemplate, id=template_id)
        
        # Crear código único para el clon
        base_code = f"{original.code}-copia"
        code = base_code
        counter = 1
        while ProductTemplate.objects.filter(code=code).exists():
            code = f"{base_code}-{counter}"
            counter += 1
        
        # Crear plantilla clonada
        cloned = ProductTemplate.objects.create(
            product_class=original.product_class,
            category=original.category,
            line_name=f"{original.line_name} (Copia)",
            code=code,
            base_price_net=original.base_price_net,
            currency=original.currency,
            requires_dimensions=original.requires_dimensions,
            is_active=False,  # Inactiva por defecto
            version=1,
            legacy_product_id=original.legacy_product_id,
            legacy_extrusora_id=original.legacy_extrusora_id,
            legacy_extrusora_name=original.legacy_extrusora_name,
            legacy_metadata=original.legacy_metadata,
        )
        
        # Clonar atributos y opciones
        for attr in original.attributes.all():
            cloned_attr = attr
            cloned_attr.pk = None
            cloned_attr.template = cloned
            cloned_attr.save()
            
            for option in attr.options.all():
                option.pk = None
                option.attribute = cloned_attr
                option.save()
        
        return JsonResponse({
            'success': True,
            'template': {
                'id': cloned.id,
                'code': cloned.code,
                'line_name': cloned.line_name,
                'product_class': cloned.product_class,
                'is_active': cloned.is_active,
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_template(request, template_id):
    """API para eliminar plantilla"""
    try:
        template = get_object_or_404(ProductTemplate, id=template_id)
        
        # Verificar que no esté siendo usada en presupuestos
        from apps.sales.models import LineaPresupuesto
        if LineaPresupuesto.objects.filter(template=template).exists():
            return JsonResponse({
                'error': 'No se puede eliminar: plantilla en uso en presupuestos'
            }, status=400)
        
        template_info = {
            'id': template.id,
            'code': template.code,
            'line_name': template.line_name,
        }
        
        template.delete()
        
        return JsonResponse({
            'success': True,
            'deleted_template': template_info
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)