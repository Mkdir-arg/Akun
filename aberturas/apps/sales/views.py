from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Presupuesto, LineaPresupuesto
from apps.catalog.models import ProductTemplate
from apps.crm.models import Cliente
import json

@login_required
def presupuesto_list(request):
    """Lista de presupuestos"""
    presupuestos = Presupuesto.objects.select_related('customer', 'created_by').all()
    return render(request, 'sales/presupuesto_list.html', {
        'presupuestos': presupuestos
    })

@login_required
def presupuesto_detail(request, pk):
    """Detalle de presupuesto"""
    presupuesto = get_object_or_404(Presupuesto, pk=pk)
    return render(request, 'sales/presupuesto_detail.html', {
        'presupuesto': presupuesto
    })

@login_required
def presupuesto_create(request):
    """Crear nuevo presupuesto"""
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        description = request.POST.get('description', '')
        
        if not customer_id:
            messages.error(request, 'Cliente requerido')
            return redirect('sales:presupuesto_create')
        
        customer = get_object_or_404(Cliente, pk=customer_id)
        
        presupuesto = Presupuesto.objects.create(
            customer=customer,
            created_by=request.user,
            description=description
        )
        
        messages.success(request, f'Presupuesto {presupuesto.number} creado exitosamente')
        return redirect('sales:presupuesto_detail', pk=presupuesto.pk)
    
    clientes = Cliente.objects.filter(is_active=True).order_by('name')
    return render(request, 'sales/presupuesto_form.html', {
        'clientes': clientes
    })

@login_required
def presupuesto_add_item(request, pk):
    """Agregar ítem basado en plantilla al presupuesto"""
    presupuesto = get_object_or_404(Presupuesto, pk=pk)
    
    if request.method == 'POST':
        template_id = request.POST.get('template_id')
        template_config = request.POST.get('template_config', '{}')
        quantity = request.POST.get('quantity', 1)
        
        if not template_id:
            messages.error(request, 'Plantilla requerida')
            return redirect('sales:presupuesto_add_item', pk=pk)
        
        try:
            template = ProductTemplate.objects.get(pk=template_id)
            config = json.loads(template_config)
            
            # Obtener el siguiente número de línea
            last_line = presupuesto.items.order_by('-line_number').first()
            line_number = (last_line.line_number + 1) if last_line else 1
            
            # Crear línea de presupuesto
            LineaPresupuesto.objects.create(
                quote=presupuesto,
                template=template,
                template_config=config,
                quantity=quantity,
                line_number=line_number
            )
            
            messages.success(request, 'Ítem agregado al presupuesto')
            return redirect('sales:presupuesto_detail', pk=pk)
            
        except (ProductTemplate.DoesNotExist, json.JSONDecodeError) as e:
            messages.error(request, f'Error: {str(e)}')
    
    templates = ProductTemplate.objects.filter(is_active=True).order_by('line_name', 'product_class')
    return render(request, 'sales/presupuesto_add_item.html', {
        'presupuesto': presupuesto,
        'templates': templates
    })

@csrf_exempt
@require_http_methods(["POST"])
def add_template_item(request):
    """API para agregar ítem basado en plantilla"""
    try:
        data = json.loads(request.body)
        
        presupuesto_id = data.get('presupuesto_id')
        template_id = data.get('template_id')
        template_config = data.get('template_config', {})
        quantity = data.get('quantity', 1)
        
        if not all([presupuesto_id, template_id]):
            return JsonResponse({'error': 'Presupuesto ID y Template ID requeridos'}, status=400)
        
        presupuesto = get_object_or_404(Presupuesto, pk=presupuesto_id)
        template = get_object_or_404(ProductTemplate, pk=template_id)
        
        # Obtener el siguiente número de línea
        last_line = presupuesto.items.order_by('-line_number').first()
        line_number = (last_line.line_number + 1) if last_line else 1
        
        # Crear línea de presupuesto
        linea = LineaPresupuesto.objects.create(
            quote=presupuesto,
            template=template,
            template_config=template_config,
            quantity=quantity,
            line_number=line_number
        )
        
        return JsonResponse({
            'success': True,
            'line_id': linea.id,
            'line_number': linea.line_number,
            'description': linea.description,
            'unit_price': float(linea.unit_price),
            'total': float(linea.total),
            'presupuesto_total': float(presupuesto.total)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_templates(request):
    """API para obtener plantillas disponibles"""
    product_class = request.GET.get('product_class')
    
    templates = ProductTemplate.objects.filter(is_active=True)
    
    if product_class:
        templates = templates.filter(product_class=product_class)
    
    templates_data = []
    for template in templates:
        templates_data.append({
            'id': template.id,
            'code': template.code,
            'line_name': template.line_name,
            'product_class': template.product_class,
            'requires_dimensions': template.requires_dimensions,
            'base_price_net': float(template.base_price_net)
        })
    
    return JsonResponse({'templates': templates_data})

@require_http_methods(["GET"])
def get_template_detail(request, template_id):
    """API para obtener detalle de una plantilla específica"""
    try:
        template = get_object_or_404(ProductTemplate, pk=template_id)
        
        # Obtener atributos con opciones
        attributes_data = []
        for attr in template.attributes.all().order_by('order'):
            attr_data = {
                'id': attr.id,
                'name': attr.name,
                'code': attr.code,
                'type': attr.type,
                'is_required': attr.is_required,
                'order': attr.order
            }
            
            if attr.type == 'SELECT':
                attr_data['options'] = [
                    {
                        'id': opt.id,
                        'code': opt.code,
                        'label': opt.label,
                        'price_value': float(opt.price_value),
                        'order': opt.order
                    }
                    for opt in attr.options.all().order_by('order')
                ]
            
            attributes_data.append(attr_data)
        
        template_data = {
            'id': template.id,
            'code': template.code,
            'line_name': template.line_name,
            'product_class': template.product_class,
            'requires_dimensions': template.requires_dimensions,
            'base_price_net': float(template.base_price_net),
            'is_active': template.is_active,
            'version': template.version,
            'attributes': attributes_data
        }
        
        return JsonResponse({'template': template_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def calculate_template_price(request):
    """API para calcular precio de plantilla con configuración específica"""
    try:
        data = json.loads(request.body)
        
        template_id = data.get('template_id')
        template_config = data.get('template_config', {})
        quantity = data.get('quantity', 1)
        
        if not template_id:
            return JsonResponse({'error': 'Template ID requerido'}, status=400)
        
        template = get_object_or_404(ProductTemplate, pk=template_id)
        
        # Calcular precio usando el método de AttributeOption
        from apps.catalog.models import AttributeOption
        pricing = AttributeOption.calculate_pricing(template_id, template_config)
        
        # Calcular total con cantidad
        unit_price = pricing['price']['gross']
        total_price = unit_price * quantity
        
        return JsonResponse({
            'success': True,
            'unit_price': unit_price,
            'total_price': total_price,
            'quantity': quantity,
            'pricing_details': pricing
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)