"""
Repository layer for contacts application.
Implements Repository pattern following Dependency Inversion Principle.
"""

from typing import Protocol, Optional
from django.db.models import QuerySet

from apps.contacts.models import Contact


class ContactRepositoryInterface(Protocol):
    """
    Abstract interface for Contact repository.
    Defines contract for data access operations (Interface Segregation).
    """
    
    def get_all(self) -> QuerySet[Contact]:
        """Retrieve all contacts."""
        ...
    
    def get_by_id(self, contact_id: int) -> Optional[Contact]:
        """Retrieve contact by ID."""
        ...
    
    def get_by_email(self, email: str) -> Optional[Contact]:
        """Retrieve contact by email."""
        ...
    
    def get_active(self) -> QuerySet[Contact]:
        """Retrieve only active contacts."""
        ...
    
    def create(self, name: str, email: str, phone: str, status: str) -> Contact:
        """Create new contact."""
        ...
    
    def update(self, contact: Contact, **kwargs) -> Contact:
        """Update existing contact."""
        ...
    
    def delete(self, contact_id: int) -> bool:
        """Delete contact by ID."""
        ...
    
    def exists_by_email(self, email: str) -> bool:
        """Check if contact with email exists."""
        ...


class DjangoContactRepository:
    """
    Concrete implementation of Contact repository using Django ORM.
    Can be easily replaced with other implementations (Liskov Substitution).
    """
    
    def get_all(self) -> QuerySet[Contact]:
        """Retrieve all contacts ordered by creation date."""
        return Contact.objects.all().order_by('-created_at')
    
    def get_by_id(self, contact_id: int) -> Optional[Contact]:
        """
        Retrieve contact by ID.
        
        Args:
            contact_id: Primary key of the contact
            
        Returns:
            Contact instance or None if not found
        """
        try:
            return Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return None
    
    def get_by_email(self, email: str) -> Optional[Contact]:
        """
        Retrieve contact by email address.
        
        Args:
            email: Email address to search
            
        Returns:
            Contact instance or None if not found
        """
        try:
            return Contact.objects.get(email=email)
        except Contact.DoesNotExist:
            return None
    
    def get_active(self) -> QuerySet[Contact]:
        """Retrieve only active contacts."""
        return Contact.objects.filter(
            status=Contact.STATUS_ACTIVE
        ).order_by('-created_at')
    
    def create(self, name: str, email: str, phone: str, status: str) -> Contact:
        """
        Create new contact.
        
        Args:
            name: Contact full name
            email: Contact email address
            phone: Contact phone number
            status: Contact status (active/inactive)
            
        Returns:
            Created Contact instance
        """
        contact = Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            status=status
        )
        return contact
    
    def update(self, contact: Contact, **kwargs) -> Contact:
        """
        Update existing contact.
        
        Args:
            contact: Contact instance to update
            **kwargs: Fields to update
            
        Returns:
            Updated Contact instance
        """
        for field, value in kwargs.items():
            if hasattr(contact, field):
                setattr(contact, field, value)
        
        contact.save()
        return contact
    
    def delete(self, contact_id: int) -> bool:
        """
        Delete contact by ID.
        
        Args:
            contact_id: Primary key of the contact
            
        Returns:
            True if deleted, False if not found
        """
        try:
            contact = Contact.objects.get(id=contact_id)
            contact.delete()
            return True
        except Contact.DoesNotExist:
            return False
    
    def exists_by_email(self, email: str) -> bool:
        """
        Check if contact with given email exists.
        
        Args:
            email: Email address to check
            
        Returns:
            True if exists, False otherwise
        """
        return Contact.objects.filter(email=email).exists()
