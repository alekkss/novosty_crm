"""
Models for logs application.
Stores frontend and application logs for monitoring and debugging.

Single Responsibility: отвечает только за структуру данных логов
"""
from django.db import models
from django.utils import timezone


class FrontendLog(models.Model):
    """
    Модель для хранения логов с frontend.
    
    Хранит JavaScript ошибки, warnings и другие события
    для централизованного мониторинга.
    """
    
    # Уровни логирования
    LEVEL_DEBUG = 'debug'
    LEVEL_INFO = 'info'
    LEVEL_WARNING = 'warning'
    LEVEL_ERROR = 'error'
    LEVEL_CRITICAL = 'critical'
    
    LEVEL_CHOICES = [
        (LEVEL_DEBUG, 'Debug'),
        (LEVEL_INFO, 'Info'),
        (LEVEL_WARNING, 'Warning'),
        (LEVEL_ERROR, 'Error'),
        (LEVEL_CRITICAL, 'Critical'),
    ]
    
    # Основные поля
    level = models.CharField(
        max_length=10,
        choices=LEVEL_CHOICES,
        default=LEVEL_INFO,
        db_index=True,
        verbose_name='Уровень'
    )
    
    message = models.TextField(
        verbose_name='Сообщение'
    )
    
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name='Время'
    )
    
    # Информация об ошибке (если это error/critical)
    error_type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Тип ошибки'
    )
    
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='Сообщение ошибки'
    )
    
    stack_trace = models.TextField(
        null=True,
        blank=True,
        verbose_name='Stack trace'
    )
    
    # Контекст
    url = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='URL страницы'
    )
    
    user_agent = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='User Agent'
    )
    
    browser = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Браузер'
    )
    
    browser_version = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Версия браузера'
    )
    
    os = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Операционная система'
    )
    
    screen_resolution = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Разрешение экрана'
    )
    
    # Дополнительные данные в JSON формате
    context = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Дополнительный контекст'
    )
    
    # Информация о пользователе (если доступна)
    user_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name='ID пользователя'
    )
    
    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name='ID сессии'
    )
    
    # Служебные поля
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP адрес'
    )
    
    request_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        verbose_name='Request ID'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    
    # Флаги для фильтрации
    is_resolved = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Решено'
    )
    
    is_ignored = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Игнорировать'
    )
    
    class Meta:
        db_table = 'frontend_logs'
        verbose_name = 'Frontend лог'
        verbose_name_plural = 'Frontend логи'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'level']),
            models.Index(fields=['level', 'is_resolved']),
            models.Index(fields=['user_id', '-timestamp']),
        ]
    
    def __str__(self) -> str:
        """String representation."""
        return f"[{self.level.upper()}] {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {self.message[:50]}"
    
    def mark_as_resolved(self) -> None:
        """Пометить лог как решенный."""
        self.is_resolved = True
        self.save(update_fields=['is_resolved'])
    
    def mark_as_ignored(self) -> None:
        """Пометить лог как игнорируемый."""
        self.is_ignored = True
        self.save(update_fields=['is_ignored'])
    
    @classmethod
    def get_unresolved_errors(cls):
        """
        Получить нерешенные ошибки.
        
        Returns:
            QuerySet нерешенных ошибок
        """
        return cls.objects.filter(
            level__in=[cls.LEVEL_ERROR, cls.LEVEL_CRITICAL],
            is_resolved=False,
            is_ignored=False
        )
    
    @classmethod
    def get_recent_by_level(cls, level: str, hours: int = 24):
        """
        Получить последние логи определенного уровня.
        
        Args:
            level: Уровень логирования
            hours: За сколько часов (по умолчанию 24)
        
        Returns:
            QuerySet логов
        """
        from datetime import timedelta
        
        since = timezone.now() - timedelta(hours=hours)
        return cls.objects.filter(
            level=level,
            timestamp__gte=since
        )
    
    @classmethod
    def cleanup_old_logs(cls, days: int = 30) -> int:
        """
        Удалить старые логи.
        
        Args:
            days: Удалить логи старше N дней
        
        Returns:
            Количество удаленных записей
        """
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        count, _ = cls.objects.filter(
            timestamp__lt=cutoff_date,
            is_resolved=True
        ).delete()
        
        return count
