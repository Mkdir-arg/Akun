from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ProductTemplate, TemplateAttribute, AttributeOption
from .serializers import ProductTemplateSerializer, TemplateAttributeSerializer, AttributeOptionSerializer

class ProductTemplateViewSet(viewsets.ModelViewSet):
    queryset = ProductTemplate.objects.all()
    serializer_class = ProductTemplateSerializer
    permission_classes = [IsAuthenticated]

class TemplateAttributeViewSet(viewsets.ModelViewSet):
    queryset = TemplateAttribute.objects.all()
    serializer_class = TemplateAttributeSerializer
    permission_classes = [IsAuthenticated]

class AttributeOptionViewSet(viewsets.ModelViewSet):
    queryset = AttributeOption.objects.all()
    serializer_class = AttributeOptionSerializer
    permission_classes = [IsAuthenticated]