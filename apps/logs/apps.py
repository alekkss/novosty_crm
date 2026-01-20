"""
Application configuration for logs app.
"""
from django.apps import AppConfig


class LogsConfig(AppConfig):
    """Configuration for logs application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.logs'
    verbose_name = 'Логи'
