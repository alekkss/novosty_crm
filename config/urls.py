"""
URL Configuration for novosty_crm project.
Routes are organized by responsibility following SOLID principles.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # API endpoints (delegated to contacts app)
    path('api/', include('apps.contacts.urls')),
    path('api/logs/', include('apps.logs.urls')),  # Добавить эту строку
    
    # Frontend (serves static HTML)
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('', include('apps.contacts.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
