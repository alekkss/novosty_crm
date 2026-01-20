"""
Admin configuration for logs application.
"""
from django.contrib import admin
from apps.logs.models import FrontendLog


@admin.register(FrontendLog)
class FrontendLogAdmin(admin.ModelAdmin):
    """Admin interface for FrontendLog model."""
    
    list_display = [
        'id',
        'level',
        'message_short',
        'timestamp',
        'url_short',
        'user_id',
        'is_resolved',
    ]
    
    list_filter = [
        'level',
        'is_resolved',
        'is_ignored',
        'timestamp',
        'browser',
        'os',
    ]
    
    search_fields = [
        'message',
        'error_message',
        'url',
        'user_id',
        'request_id',
    ]
    
    readonly_fields = [
        'timestamp',
        'created_at',
        'ip_address',
        'request_id',
    ]
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'level',
                'message',
                'timestamp',
            )
        }),
        ('Информация об ошибке', {
            'fields': (
                'error_type',
                'error_message',
                'stack_trace',
            ),
            'classes': ('collapse',)
        }),
        ('Контекст', {
            'fields': (
                'url',
                'context',
                'user_id',
                'session_id',
                'request_id',
            )
        }),
        ('Браузер и система', {
            'fields': (
                'user_agent',
                'browser',
                'browser_version',
                'os',
                'screen_resolution',
            ),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': (
                'ip_address',
                'created_at',
                'is_resolved',
                'is_ignored',
            )
        }),
    )
    
    actions = ['mark_as_resolved', 'mark_as_ignored']
    
    def message_short(self, obj):
        """Короткое сообщение."""
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_short.short_description = 'Сообщение'
    
    def url_short(self, obj):
        """Короткий URL."""
        if not obj.url:
            return '-'
        return obj.url[:50] + '...' if len(obj.url) > 50 else obj.url
    url_short.short_description = 'URL'
    
    def mark_as_resolved(self, request, queryset):
        """Пометить как решенные."""
        count = queryset.update(is_resolved=True)
        self.message_user(request, f'Помечено как решенные: {count} логов')
    mark_as_resolved.short_description = 'Пометить как решенные'
    
    def mark_as_ignored(self, request, queryset):
        """Пометить как игнорируемые."""
        count = queryset.update(is_ignored=True)
        self.message_user(request, f'Помечено как игнорируемые: {count} логов')
    mark_as_ignored.short_description = 'Пометить как игнорируемые'
