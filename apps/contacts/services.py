"""
Service layer for contacts application.
Implements business logic and validation following SOLID principles.
"""

from typing import Optional
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from apps.contacts.models import Contact
from apps.contacts.repositories import ContactRepositoryInterface, DjangoContactRepository


class ContactService:
    """
    Service for managing contacts business logic.
    Depends on repository abstraction (Dependency Inversion Principle).
    """
    
    def __init__(self, repository: ContactRepositoryInterface) -> None:
        """
        Initialize service with repository dependency.
        
        Args:
            repository: Implementation of ContactRepositoryInterface
        """
        self._repository = repository
    
    def get_all_contacts(self) -> list[dict]:
        """
        Retrieve all contacts as list of dictionaries.
        
        Returns:
            List of contact dictionaries for API response
        """
        contacts = self._repository.get_all()
        return self._serialize_contacts(contacts)
    
    def get_active_contacts(self) -> list[dict]:
        """
        Retrieve only active contacts.
        
        Returns:
            List of active contact dictionaries
        """
        contacts = self._repository.get_active()
        return self._serialize_contacts(contacts)
    
    def get_contact_by_id(self, contact_id: int) -> Optional[dict]:
        """
        Retrieve single contact by ID.
        
        Args:
            contact_id: Primary key of the contact
            
        Returns:
            Contact dictionary or None if not found
        """
        contact = self._repository.get_by_id(contact_id)
        if contact is None:
            return None
        return self._serialize_contact(contact)
    
    def create_contact(
        self,
        name: str,
        email: str,
        phone: str,
        status: str = Contact.STATUS_ACTIVE
    ) -> dict:
        """
        Create new contact with validation.
        
        Args:
            name: Contact full name
            email: Contact email address
            phone: Contact phone number
            status: Contact status (default: active)
            
        Returns:
            Created contact dictionary
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate input data
        self._validate_contact_data(name, email, phone, status)
        
        # Check email uniqueness
        if self._repository.exists_by_email(email):
            raise ValidationError({
                'email': 'Контакт с таким email уже существует'
            })
        
        # Create contact
        contact = self._repository.create(
            name=name.strip(),
            email=email.strip().lower(),
            phone=phone.strip(),
            status=status
        )
        
        return self._serialize_contact(contact)
    
    def update_contact(
        self,
        contact_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[dict]:
        """
        Update existing contact.
        
        Args:
            contact_id: Primary key of the contact
            name: New name (optional)
            email: New email (optional)
            phone: New phone (optional)
            status: New status (optional)
        
        Returns:
            Updated contact dictionary or None if not found
        
        Raises:
            ValidationError: If validation fails
        """
        print(f"!!! UPDATE_CONTACT: id={contact_id}, email={repr(email)}")
        contact = self._repository.get_by_id(contact_id)
        if contact is None:
            return None
        
        # Prepare update data
        update_data = {}
        
        if name is not None:
            update_data['name'] = name.strip()
        
        if email is not None:
            email = email.strip().lower()

            
            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError({'email': 'Некорректный email адрес'})
            
            # Check uniqueness ONLY if email changed
            with open('/tmp/debug_email.log', 'a') as f:
                f.write(f"=== EMAIL CHECK ===\n")
                f.write(f"new email: |{email}|\n")
                f.write(f"contact.email: |{contact.email}|\n")
                f.write(f"contact.email.lower(): |{contact.email.lower()}|\n")
                f.write(f"equal? {email == contact.email.lower()}\n")
                f.write(f"contact_id param: {contact_id}\n")
                f.write(f"contact.id: {contact.id}\n\n")

            if email != contact.email.lower():
                existing = self._repository.get_by_email(email)
                
                with open('/tmp/debug_email.log', 'a') as f:
                    f.write(f"Email changed! Checking uniqueness...\n")
                    f.write(f"existing: {existing}\n")
                    if existing:
                        f.write(f"existing.id: {existing.id}\n")
                        f.write(f"contact_id: {contact_id}\n")
                        f.write(f"existing.id != contact_id: {existing.id != contact_id}\n\n")
                
                if existing and existing.id != contact_id:
                    raise ValidationError({'email': 'Контакт с таким email уже существует'})

            update_data['email'] = email
        
        if phone is not None:
            update_data['phone'] = phone.strip()
        
        if status is not None:
            if status not in [Contact.STATUS_ACTIVE, Contact.STATUS_INACTIVE]:
                raise ValidationError({
                    'status': f'Недопустимый статус. Используйте: {Contact.STATUS_ACTIVE} или {Contact.STATUS_INACTIVE}'
                })
            update_data['status'] = status
        
        # Update contact
        updated_contact = self._repository.update(contact, **update_data)
        return self._serialize_contact(updated_contact)
    
    def delete_contact(self, contact_id: int) -> bool:
        """
        Delete contact by ID.
        
        Args:
            contact_id: Primary key of the contact
            
        Returns:
            True if deleted, False if not found
        """
        return self._repository.delete(contact_id)
    
    def _validate_contact_data(
        self,
        name: str,
        email: str,
        phone: str,
        status: str
    ) -> None:
        """
        Validate contact data.
        
        Args:
            name: Contact name
            email: Contact email
            phone: Contact phone
            status: Contact status
            
        Raises:
            ValidationError: If any field is invalid
        """
        errors = {}
        
        # Validate name
        if not name or not name.strip():
            errors['name'] = 'Имя обязательно для заполнения'
        elif len(name.strip()) < 2:
            errors['name'] = 'Имя должно содержать минимум 2 символа'
        
        # Validate email
        if not email or not email.strip():
            errors['email'] = 'Email обязателен для заполнения'
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors['email'] = 'Некорректный email адрес'
        
        # Validate phone
        if not phone or not phone.strip():
            errors['phone'] = 'Телефон обязателен для заполнения'
        elif len(phone.strip()) < 10:
            errors['phone'] = 'Телефон должен содержать минимум 10 символов'
        
        # Validate status
        if status not in [Contact.STATUS_ACTIVE, Contact.STATUS_INACTIVE]:
            errors['status'] = f'Недопустимый статус. Используйте: {Contact.STATUS_ACTIVE} или {Contact.STATUS_INACTIVE}'
        
        if errors:
            raise ValidationError(errors)
    
    def _serialize_contact(self, contact: Contact) -> dict:
        """
        Serialize single contact to dictionary.
        
        Args:
            contact: Contact instance
            
        Returns:
            Contact dictionary
        """
        return {
            'id': contact.id,
            'name': contact.name,
            'email': contact.email,
            'phone': contact.phone,
            'status': contact.status,
        }
    
    def _serialize_contacts(self, contacts: QuerySet[Contact]) -> list[dict]:
        """
        Serialize multiple contacts to list of dictionaries.
        
        Args:
            contacts: QuerySet of contacts
            
        Returns:
            List of contact dictionaries
        """
        return [self._serialize_contact(contact) for contact in contacts]


# Factory function for creating service instance with default repository
def get_contact_service() -> ContactService:
    """
    Factory function to create ContactService with default repository.
    Facilitates dependency injection (Dependency Inversion Principle).
    
    Returns:
        ContactService instance
    """
    repository = DjangoContactRepository()
    return ContactService(repository)
