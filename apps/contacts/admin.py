"""
Django Admin configuration for contacts application.
Provides user-friendly interface for managing contacts.
"""

from django.contrib import admin
from django.utils.html import format_html
from typing import Any

from apps.contacts.models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin interface for Contact model.
    Implements Single Responsibility - handles only admin UI configuration.
    """
    
    # List display configuration
    list_display = [
        'id',
        'name',
        'email',
        'phone',
        'status_badge',
        'created_at',
    ]
    
    # Filters
    list_filter = [
        'status',
        'created_at',
    ]
    
    # Search fields
    search_fields = [
        'name',
        'email',
        'phone',
    ]
    
    # Ordering
    ordering = ['-created_at']
    
    # Read-only fields
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    
    # Fieldsets for detail view
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Статус', {
            'fields': ('status',)
        }),
        ('Системная информация', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # List per page
    list_per_page = 50
    
    # Actions
    actions = [
        'activate_contacts',
        'deactivate_contacts',
    ]
    
    def status_badge(self, obj: Contact) -> str:
        """
        Display status as colored badge.
        
        Args:
            obj: Contact instance
            
        Returns:
            HTML formatted status badge
        """
        if obj.status == Contact.STATUS_ACTIVE:
            color = '#28a745'  # Green
            text = 'Активный'
        else:
            color = '#dc3545'  # Red
            text = 'Неактивный'
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            text
        )
    
    status_badge.short_description = 'Статус'
    
    @admin.action(description='Активировать выбранные контакты')
    def activate_contacts(self, request: Any, queryset: Any) -> None:
        """
        Bulk action to activate selected contacts.
        
        Args:
            request: HTTP request
            queryset: Selected contacts queryset
        """
        updated = queryset.update(status=Contact.STATUS_ACTIVE)
        self.message_user(
            request,
            f'Активировано контактов: {updated}'
        )
    
    @admin.action(description='Деактивировать выбранные контакты')
    def deactivate_contacts(self, request: Any, queryset: Any) -> None:
        """
        Bulk action to deactivate selected contacts.
        
        Args:
            request: HTTP request
            queryset: Selected contacts queryset
        """
        updated = queryset.update(status=Contact.STATUS_INACTIVE)
        self.message_user(
            request,
            f'Деактивировано контактов: {updated}'
        )
