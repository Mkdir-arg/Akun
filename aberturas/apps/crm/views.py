from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import RoleBasedPermission
from django.db.models import Q
from django.db import transaction
from .models import Cliente, Direccion, Contacto, TerminoPago, EtiquetaCliente, NotaCliente, ArchivoCliente
from .serializers import (
    ClienteSerializer, ClienteDetailSerializer, DireccionSerializer,
    ContactoSerializer, TerminoPagoSerializer, EtiquetaClienteSerializer,
    NotaClienteSerializer, ArchivoClienteSerializer
)


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.select_related('default_price_list', 'payment_terms').prefetch_related('tags')
    permission_classes = []  # Temporalmente sin permisos
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'tax_id', 'email', 'phone']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClienteDetailSerializer
        return ClienteSerializer
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        customer = self.get_object()
        customer.status = 'ACTIVO'
        customer.is_active = True
        customer.save()
        return Response({'status': 'Cliente activado'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        customer = self.get_object()
        customer.status = 'INACTIVO'
        customer.is_active = False
        customer.save()
        return Response({'status': 'Cliente desactivado'})
    
    @action(detail=True, methods=['post'])
    def set_default_address(self, request, pk=None):
        customer = self.get_object()
        kind = request.data.get('kind')
        address_id = request.data.get('address_id')
        
        try:
            with transaction.atomic():
                # Desmarcar direcciones default del mismo tipo
                Direccion.objects.filter(customer=customer, kind=kind).update(is_default=False)
                # Marcar nueva dirección como default
                address = Direccion.objects.get(id=address_id, customer=customer)
                address.is_default = True
                address.save()
                
            return Response({'status': 'Dirección por defecto actualizada'})
        except Direccion.DoesNotExist:
            return Response({'error': 'Dirección no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def set_primary_contact(self, request, pk=None):
        customer = self.get_object()
        contact_id = request.data.get('contact_id')
        
        try:
            with transaction.atomic():
                # Desmarcar contactos primarios
                Contacto.objects.filter(customer=customer).update(is_primary=False)
                # Marcar nuevo contacto como primario
                contact = Contacto.objects.get(id=contact_id, customer=customer)
                contact.is_primary = True
                contact.save()
                
            return Response({'status': 'Contacto principal actualizado'})
        except Contacto.DoesNotExist:
            return Response({'error': 'Contacto no encontrado'}, status=status.HTTP_404_NOT_FOUND)


class DireccionViewSet(viewsets.ModelViewSet):
    serializer_class = DireccionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Direccion.objects.select_related('customer')


class ContactoViewSet(viewsets.ModelViewSet):
    serializer_class = ContactoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Contacto.objects.select_related('customer')


class TerminoPagoViewSet(viewsets.ModelViewSet):
    queryset = TerminoPago.objects.filter(is_active=True)
    serializer_class = TerminoPagoSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['days']


class EtiquetaClienteViewSet(viewsets.ModelViewSet):
    queryset = EtiquetaCliente.objects.filter(is_active=True)
    serializer_class = EtiquetaClienteSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['name']


class NotaClienteViewSet(viewsets.ModelViewSet):
    serializer_class = NotaClienteSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-pinned', '-created_at']
    
    def get_queryset(self):
        return NotaCliente.objects.select_related('customer', 'author')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ArchivoClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ArchivoClienteSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-uploaded_at']
    
    def get_queryset(self):
        return ArchivoCliente.objects.select_related('customer', 'uploaded_by')
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        file_obj = self.get_object()
        response = Response()
        response['Content-Disposition'] = f'attachment; filename="{file_obj.file.name}"'
        response['X-Accel-Redirect'] = file_obj.file.url
        return response