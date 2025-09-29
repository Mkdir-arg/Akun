from django.http import JsonResponse
from django.db.models import Q
from .models import Provincia, Municipio, Localidad


def provincias_list(request):
    """Lista todas las provincias"""
    search = request.GET.get('search', '')
    
    provincias = Provincia.objects.all()
    
    if search:
        provincias = provincias.filter(nombre__icontains=search)
    
    data = [{'id': p.id, 'nombre': p.nombre} for p in provincias[:50]]
    return JsonResponse(data, safe=False)


def municipios_list(request):
    """Lista municipios filtrados por provincia"""
    provincia_id = request.GET.get('provincia_id')
    search = request.GET.get('search', '')
    
    municipios = Municipio.objects.select_related('provincia')
    
    if provincia_id:
        municipios = municipios.filter(provincia_id=provincia_id)
    
    if search:
        municipios = municipios.filter(nombre__icontains=search)
    
    data = [{'id': m.id, 'nombre': m.nombre, 'provincia_id': m.provincia_id} for m in municipios[:50]]
    return JsonResponse(data, safe=False)


def localidades_list(request):
    """Lista localidades filtradas por municipio"""
    municipio_id = request.GET.get('municipio_id')
    search = request.GET.get('search', '')
    
    localidades = Localidad.objects.select_related('municipio__provincia')
    
    if municipio_id:
        localidades = localidades.filter(municipio_id=municipio_id)
    
    if search:
        localidades = localidades.filter(nombre__icontains=search)
    
    data = [{'id': l.id, 'nombre': l.nombre, 'municipio_id': l.municipio_id} for l in localidades[:50]]
    return JsonResponse(data, safe=False)