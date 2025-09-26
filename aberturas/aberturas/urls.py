"""
URL configuration for aberturas project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.ui.urls')),
    path('', include('apps.accounts.urls')),
    path('', include('apps.crm.urls')),
    path('', include('apps.catalog.urls')),
    path('catalog/', include('apps.catalog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass