"""
Domain models for contacts application.
Each model represents a single business entity (Single Responsibility).
"""

from django.db import models
from typing import ClassVar


class Contact(models.Model):
    """
    Contact model representing a CRM contact entry.
    
    Attributes:
        name: Full name of the contact
        email: Email address (unique)
        phone: Phone number
        status: Contact status (active or inactive)
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    
    # Status choices
    STATUS_ACTIVE: ClassVar[str] = 'active'
    STATUS_INACTIVE: ClassVar[str] = 'inactive'
    
    STATUS_CHOICES: ClassVar[list[tuple[str, str]]] = [
        (STATUS_ACTIVE, 'Активный'),
        (STATUS_INACTIVE, 'Неактивный'),
    ]
    
    # Fields
    name = models.CharField(
        max_length=255,
        verbose_name='Имя',
        help_text='Полное имя контакта'
    )
    
    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        help_text='Уникальный email адрес'
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон',
        help_text='Номер телефона'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Статус',
        help_text='Текущий статус контакта'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        db_table = 'contacts'
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self) -> str:
        """String representation of the contact."""
        return f"{self.name} ({self.email})"
    
    def is_active(self) -> bool:
        """Check if contact is active."""
        return self.status == self.STATUS_ACTIVE
    
    def activate(self) -> None:
        """Set contact status to active."""
        self.status = self.STATUS_ACTIVE
    
    def deactivate(self) -> None:
        """Set contact status to inactive."""
        self.status = self.STATUS_INACTIVE
