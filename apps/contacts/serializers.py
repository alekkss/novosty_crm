"""
Serializers for contacts API.
Handles data validation and serialization (Single Responsibility).
"""

from rest_framework import serializers
from apps.contacts.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for Contact model.
    Handles both input validation and output serialization.
    """
    
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'status']
        read_only_fields = ['id']
    
    def validate_name(self, value: str) -> str:
        """
        Validate contact name.
        
        Args:
            value: Name to validate
            
        Returns:
            Cleaned name value
            
        Raises:
            serializers.ValidationError: If name is invalid
        """
        if not value or not value.strip():
            raise serializers.ValidationError('Имя обязательно для заполнения')
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Имя должно содержать минимум 2 символа')
        
        return value.strip()
    
    def validate_email(self, value: str) -> str:
        """
        Validate and normalize email.
        
        Args:
            value: Email to validate
            
        Returns:
            Normalized email (lowercase, trimmed)
            
        Raises:
            serializers.ValidationError: If email is invalid
        """
        if not value or not value.strip():
            raise serializers.ValidationError('Email обязателен для заполнения')
        
        # Normalize email
        normalized_email = value.strip().lower()
        
        # Check uniqueness for create operation
        if self.instance is None:  # Creating new contact
            if Contact.objects.filter(email=normalized_email).exists():
                raise serializers.ValidationError('Контакт с таким email уже существует')
        else:  # Updating existing contact
            if Contact.objects.filter(email=normalized_email).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError('Контакт с таким email уже существует')
        
        return normalized_email
    
    def validate_phone(self, value: str) -> str:
        """
        Validate phone number.
        
        Args:
            value: Phone to validate
            
        Returns:
            Cleaned phone value
            
        Raises:
            serializers.ValidationError: If phone is invalid
        """
        if not value or not value.strip():
            raise serializers.ValidationError('Телефон обязателен для заполнения')
        
        if len(value.strip()) < 10:
            raise serializers.ValidationError('Телефон должен содержать минимум 10 символов')
        
        return value.strip()
    
    def validate_status(self, value: str) -> str:
        """
        Validate contact status.
        
        Args:
            value: Status to validate
            
        Returns:
            Validated status value
            
        Raises:
            serializers.ValidationError: If status is invalid
        """
        if value not in [Contact.STATUS_ACTIVE, Contact.STATUS_INACTIVE]:
            raise serializers.ValidationError(
                f'Недопустимый статус. Используйте: {Contact.STATUS_ACTIVE} или {Contact.STATUS_INACTIVE}'
            )
        
        return value


class ContactCreateSerializer(serializers.Serializer):
    """
    Serializer specifically for creating contacts.
    Provides explicit control over input fields (Interface Segregation).
    """
    
    name = serializers.CharField(
        max_length=255,
        required=True,
        help_text='Полное имя контакта'
    )
    
    email = serializers.EmailField(
        required=True,
        help_text='Уникальный email адрес'
    )
    
    phone = serializers.CharField(
        max_length=20,
        required=True,
        help_text='Номер телефона'
    )
    
    status = serializers.ChoiceField(
        choices=[Contact.STATUS_ACTIVE, Contact.STATUS_INACTIVE],
        default=Contact.STATUS_ACTIVE,
        required=False,
        help_text='Статус контакта'
    )
    
    def validate_name(self, value: str) -> str:
        """Validate and clean name."""
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Имя должно содержать минимум 2 символа')
        return value.strip()
    
    def validate_email(self, value: str) -> str:
        """Validate and normalize email."""
        normalized_email = value.strip().lower()
        
        if Contact.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError('Контакт с таким email уже существует')
        
        return normalized_email
    
    def validate_phone(self, value: str) -> str:
        """Validate phone number."""
        if len(value.strip()) < 10:
            raise serializers.ValidationError('Телефон должен содержать минимум 10 символов')
        return value.strip()


class ContactListSerializer(serializers.Serializer):
    """
    Lightweight serializer for listing contacts.
    Optimized for read operations (Single Responsibility).
    """
    
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    phone = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
