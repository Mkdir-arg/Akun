from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.db import transaction
from .models import Customer, Address, Contact, PaymentTerm, CustomerTag, CustomerNote, CustomerFile
from .serializers import (
    CustomerSerializer, CustomerDetailSerializer, AddressSerializer,
    ContactSerializer, PaymentTermSerializer, CustomerTagSerializer,
    CustomerNoteSerializer, CustomerFileSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.select_related('default_price_list', 'payment_terms').prefetch_related('tags')
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'tax_id', 'email', 'phone']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CustomerDetailSerializer
        return CustomerSerializer
    
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
                Address.objects.filter(customer=customer, kind=kind).update(is_default=False)
                # Marcar nueva dirección como default
                address = Address.objects.get(id=address_id, customer=customer)
                address.is_default = True
                address.save()
                
            return Response({'status': 'Dirección por defecto actualizada'})
        except Address.DoesNotExist:
            return Response({'error': 'Dirección no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def set_primary_contact(self, request, pk=None):
        customer = self.get_object()
        contact_id = request.data.get('contact_id')
        
        try:
            with transaction.atomic():
                # Desmarcar contactos primarios
                Contact.objects.filter(customer=customer).update(is_primary=False)
                # Marcar nuevo contacto como primario
                contact = Contact.objects.get(id=contact_id, customer=customer)
                contact.is_primary = True
                contact.save()
                
            return Response({'status': 'Contacto principal actualizado'})
        except Contact.DoesNotExist:
            return Response({'error': 'Contacto no encontrado'}, status=status.HTTP_404_NOT_FOUND)


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.select_related('customer')


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Contact.objects.select_related('customer')


class PaymentTermViewSet(viewsets.ModelViewSet):
    queryset = PaymentTerm.objects.filter(is_active=True)
    serializer_class = PaymentTermSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['days']


class CustomerTagViewSet(viewsets.ModelViewSet):
    queryset = CustomerTag.objects.filter(is_active=True)
    serializer_class = CustomerTagSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['name']


class CustomerNoteViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerNoteSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-pinned', '-created_at']
    
    def get_queryset(self):
        return CustomerNote.objects.select_related('customer', 'author')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CustomerFileViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerFileSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-uploaded_at']
    
    def get_queryset(self):
        return CustomerFile.objects.select_related('customer', 'uploaded_by')
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        file_obj = self.get_object()
        response = Response()
        response['Content-Disposition'] = f'attachment; filename="{file_obj.file.name}"'
        response['X-Accel-Redirect'] = file_obj.file.url
        return response