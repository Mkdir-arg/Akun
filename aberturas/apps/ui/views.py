from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'ui/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_users': 0,  # Placeholder
            'total_orders': 0,  # Placeholder
            'total_products': 0,  # Placeholder
        })
        return context


class AboutView(TemplateView):
    template_name = 'ui/about.html'


def health_check(request):
    """Vista de health check para monitoreo."""
    return JsonResponse({'status': 'ok'})


@login_required
def htmx_example(request):
    """Ejemplo básico de HTMX con filtro."""
    query = request.GET.get('q', '')
    
    # Datos de ejemplo
    items = [
        {'id': 1, 'name': 'Ventana Corrediza'},
        {'id': 2, 'name': 'Puerta Principal'},
        {'id': 3, 'name': 'Ventana Batiente'},
        {'id': 4, 'name': 'Puerta Balcón'},
    ]
    
    if query:
        items = [item for item in items if query.lower() in item['name'].lower()]
    
    if request.htmx:
        return render(request, 'ui/partials/items_list.html', {'items': items})
    
    return render(request, 'ui/htmx_example.html', {'items': items})