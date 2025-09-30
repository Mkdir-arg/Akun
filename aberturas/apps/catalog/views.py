from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal

from .models import ProductTemplate, TemplateAttribute, AttributeOption
from .serializers import (
    ProductTemplateSerializer, ProductTemplateListSerializer,
    TemplateAttributeSerializer, AttributeOptionSerializer,
    PreviewPricingRequestSerializer, ReorderSerializer
)
from .services import PricingCalculatorService


class ProductTemplateViewSet(viewsets.ModelViewSet):
    queryset = ProductTemplate.objects.all()
    permission_classes = []  # Temporalmente sin permisos
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductTemplateListSerializer
        return ProductTemplateSerializer
        
    def get_queryset(self):
        queryset = ProductTemplate.objects.all()
        
        # Filtros
        product_class = self.request.query_params.get('class')
        line_name = self.request.query_params.get('line_name')
        is_active = self.request.query_params.get('active')
        
        if product_class:
            queryset = queryset.filter(product_class=product_class)
        if line_name:
            queryset = queryset.filter(line_name__icontains=line_name)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset.order_by('-created_at')
        
    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """Clona una plantilla creando una nueva versión"""
        template = self.get_object()
        
        with transaction.atomic():
            # Crear nueva versión
            new_version = ProductTemplate.objects.filter(line_name=template.line_name).count() + 1
            new_template = ProductTemplate.objects.create(
                product_class=template.product_class,
                line_name=template.line_name,
                code=f"{template.code}-v{new_version}",
                base_price_net=template.base_price_net,
                currency=template.currency,
                requires_dimensions=template.requires_dimensions,
                version=new_version
            )
            
            # Clonar atributos y opciones
            for attr in template.attributes.all():
                new_attr = TemplateAttribute.objects.create(
                    template=new_template,
                    name=attr.name,
                    code=attr.code,
                    type=attr.type,
                    is_required=attr.is_required,
                    order=attr.order,
                    rules_json=attr.rules_json
                )
                
                for option in attr.options.all():
                    AttributeOption.objects.create(
                        attribute=new_attr,
                        label=option.label,
                        code=option.code,
                        pricing_mode=option.pricing_mode,
                        price_value=option.price_value,
                        currency=option.currency,
                        order=option.order,
                        is_default=option.is_default
                    )
                    
        serializer = ProductTemplateSerializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    @action(detail=True, methods=['post'])
    def preview_pricing(self, request, pk=None):
        """Calcula preview de precio basado en selecciones"""
        template = self.get_object()
        
        serializer = PreviewPricingRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        data = serializer.validated_data
        
        try:
            result = AttributeOption.calculate_pricing(
                template_id=template.id,
                selections=data['selections'],
                currency=data.get('currency', 'ARS'),
                iva_pct=float(data.get('iva_pct', 21.0))
            )
            return Response(result)
            
        except (ValueError, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TemplateAttributeViewSet(viewsets.ModelViewSet):
    serializer_class = TemplateAttributeSerializer
    permission_classes = []  # Temporalmente sin permisos
    
    def get_queryset(self):
        template_id = self.request.query_params.get('template_id')
        if template_id:
            return TemplateAttribute.objects.filter(template_id=template_id)
        return TemplateAttribute.objects.all()
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        template_id = self.request.query_params.get('template_id') or self.request.data.get('template_id')
        if template_id:
            context['template'] = get_object_or_404(ProductTemplate, pk=template_id)
        return context
        
    def perform_create(self, serializer):
        template_id = self.request.data.get('template_id')
        template = get_object_or_404(ProductTemplate, pk=template_id)
        serializer.save(template=template)
        
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Reordena un atributo"""
        attribute = self.get_object()
        serializer = ReorderSerializer(data=request.data)
        
        if serializer.is_valid():
            new_order = serializer.validated_data['new_order']
            attribute.order = new_order
            attribute.save()
            return Response({'status': 'reordered'})
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttributeOptionViewSet(viewsets.ModelViewSet):
    serializer_class = AttributeOptionSerializer
    permission_classes = []  # Temporalmente sin permisos
    
    def get_queryset(self):
        attribute_id = self.request.query_params.get('attribute_id')
        if attribute_id:
            return AttributeOption.objects.filter(attribute_id=attribute_id)
        return AttributeOption.objects.all()
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        attribute_id = self.request.query_params.get('attribute_id') or self.request.data.get('attribute_id')
        if attribute_id:
            context['attribute'] = get_object_or_404(TemplateAttribute, pk=attribute_id)
        return context
        
    def perform_create(self, serializer):
        attribute_id = self.request.data.get('attribute_id')
        attribute = get_object_or_404(TemplateAttribute, pk=attribute_id)
        serializer.save(attribute=attribute)
        
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Reordena una opción"""
        option = self.get_object()
        serializer = ReorderSerializer(data=request.data)
        
        if serializer.is_valid():
            new_order = serializer.validated_data['new_order']
            option.order = new_order
            option.save()
            return Response({'status': 'reordered'})
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)