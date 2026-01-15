"""
Django application configuration for contacts app.
Defines app metadata and settings (Single Responsibility).
"""

from django.apps import AppConfig


class ContactsConfig(AppConfig):
    """
    Configuration class for contacts application.
    Handles app initialization and metadata.
    """
    
    # Default primary key field type
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Application name (must match directory name)
    name = 'apps.contacts'
    
    # Human-readable name for Django Admin
    verbose_name = 'Управление контактами'
    
    def ready(self) -> None:
        """
        Method called when Django starts.
        Can be used for registering signals or performing initialization.
        """
        # Import signals here if needed in future
        # from apps.contacts import signals
        pass
