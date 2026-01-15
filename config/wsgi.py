"""
WSGI config for novosty_crm project.
Exposes the WSGI callable as a module-level variable named 'application'.
Used by WSGI servers (Gunicorn, uWSGI) to serve the application.
"""

import os
from django.core.wsgi import get_wsgi_application

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create WSGI application
application = get_wsgi_application()
