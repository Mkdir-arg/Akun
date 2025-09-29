from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Presupuesto, LineaPresupuesto, Pedido, LineaPedido
from .serializers import (
    PresupuestoSerializer, PresupuestoDetailSerializer, LineaPresupuestoSerializer,
    PedidoSerializer, PedidoDetailSerializer, LineaPedidoSerializer
)


class PresupuestoViewSet(viewsets.ModelViewSet):
    queryset = Presupuesto.objects.select_related('customer', 'created_by', 'assigned_to').prefetch_related('items')
    permission_classes = []  # Temporalmente sin permisos
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['number', 'customer__name', 'customer__tax_id']
    ordering_fields = ['number', 'created_at', 'valid_until', 'total']
    ordering = ['-created_at']
    
    def update(self, request, *args, **kwargs):
        print(f"DEBUG PATCH - Request data: {request.data}")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        print(f"DEBUG PATCH - Serializer is_valid: {serializer.is_valid()}")
        if not serializer.is_valid():
            print(f"DEBUG PATCH - Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PresupuestoDetailSerializer
        return PresupuestoSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            
        customer = self.request.query_params.get('customer')
        if customer:
            queryset = queryset.filter(customer=customer)
            
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to=assigned_to)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        print(f"DEBUG - Request data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        print(f"DEBUG - Serializer is_valid: {serializer.is_valid()}")
        if not serializer.is_valid():
            print(f"DEBUG - Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        from apps.accounts.models import User
        user = self.request.user if self.request.user.is_authenticated else User.objects.filter(is_superuser=True).first()
        serializer.save(created_by=user)
    
    @action(detail=True, methods=['post'])
    def convert_to_order(self, request, pk=None):
        """Convertir presupuesto a pedido"""
        quote = self.get_object()
        print(f"DEBUG - Converting quote {quote.id} to order")
        
        try:
            order = Pedido.create_from_quote(
                quote=quote,
                created_by=request.user if request.user.is_authenticated else None
            )
            print(f"DEBUG - Order created: {order.id} - {order.number}")
            return Response({
                'message': 'Presupuesto convertido a pedido exitosamente',
                'order_id': order.id,
                'order_number': order.number
            })
        except Exception as e:
            print(f"DEBUG - Error creating order: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Marcar presupuesto como enviado"""
        quote = self.get_object()
        quote.status = 'SENT'
        quote.save()
        return Response({'message': 'Presupuesto marcado como enviado'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprobar presupuesto"""
        quote = self.get_object()
        quote.status = 'APPROVED'
        quote.save()
        return Response({'message': 'Presupuesto aprobado'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rechazar presupuesto"""
        quote = self.get_object()
        quote.status = 'REJECTED'
        quote.save()
        return Response({'message': 'Presupuesto rechazado'})


class LineaPresupuestoViewSet(viewsets.ModelViewSet):
    serializer_class = LineaPresupuestoSerializer
    permission_classes = []  # Temporalmente sin permisos
    
    def get_queryset(self):
        queryset = LineaPresupuesto.objects.select_related('quote', 'product')
        quote_id = self.request.query_params.get('quote')
        if quote_id:
            queryset = queryset.filter(quote=quote_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        print(f"DEBUG QuoteItem - Request data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        print(f"DEBUG QuoteItem - Serializer is_valid: {serializer.is_valid()}")
        if not serializer.is_valid():
            print(f"DEBUG QuoteItem - Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.select_related('customer', 'quote', 'created_by', 'assigned_to').prefetch_related('items')
    permission_classes = []  # Temporalmente sin permisos
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['number', 'title', 'customer__name', 'customer__tax_id']
    ordering_fields = ['number', 'order_date', 'delivery_date', 'total']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PedidoDetailSerializer
        return PedidoSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        payment_status = self.request.query_params.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
            
        customer = self.request.query_params.get('customer')
        if customer:
            queryset = queryset.filter(customer=customer)
            
        order_type = self.request.query_params.get('type')
        if order_type:
            queryset = queryset.filter(type=order_type)
            
        return queryset
    
    def perform_create(self, serializer):
        from apps.accounts.models import User
        user = self.request.user if self.request.user.is_authenticated else User.objects.filter(is_superuser=True).first()
        serializer.save(created_by=user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirmar pedido"""
        order = self.get_object()
        order.status = 'CONFIRMED'
        order.save()
        return Response({'message': 'Pedido confirmado'})
    
    @action(detail=True, methods=['post'])
    def start_production(self, request, pk=None):
        """Iniciar producción"""
        order = self.get_object()
        order.status = 'IN_PRODUCTION'
        order.save()
        return Response({'message': 'Producción iniciada'})
    
    @action(detail=True, methods=['post'])
    def mark_ready(self, request, pk=None):
        """Marcar como listo"""
        order = self.get_object()
        order.status = 'READY'
        order.save()
        return Response({'message': 'Pedido marcado como listo'})
    
    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        """Marcar como entregado"""
        order = self.get_object()
        order.status = 'DELIVERED'
        order.delivered_at = timezone.now()
        order.save()
        return Response({'message': 'Pedido marcado como entregado'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar pedido"""
        order = self.get_object()
        order.status = 'CANCELLED'
        order.save()
        return Response({'message': 'Pedido cancelado'})


class LineaPedidoViewSet(viewsets.ModelViewSet):
    serializer_class = LineaPedidoSerializer
    permission_classes = []  # Temporalmente sin permisos
    
    def get_queryset(self):
        queryset = LineaPedido.objects.select_related('order', 'product')
        order_id = self.request.query_params.get('order')
        if order_id:
            queryset = queryset.filter(order=order_id)
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_production_status(self, request, pk=None):
        """Actualizar estado de producción"""
        item = self.get_object()
        new_status = request.data.get('production_status')
        
        if new_status in ['PENDING', 'IN_PROGRESS', 'COMPLETED']:
            item.production_status = new_status
            item.save()
            return Response({'message': f'Estado actualizado a {new_status}'})
        
        return Response(
            {'error': 'Estado de producción inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )