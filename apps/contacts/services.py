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
from apps.core.logger import get_logger, log_execution


# Инициализируем логгер для этого модуля
logger = get_logger(__name__)


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
        self._logger = get_logger(__name__)

    def get_all_contacts(self) -> list[dict]:
        """
        Retrieve all contacts as list of dictionaries.
        
        Returns:
            List of contact dictionaries for API response
        """
        try:
            self._logger.info("Fetching all contacts")
            contacts = self._repository.get_all()
            result = self._serialize_contacts(contacts)
            
            self._logger.info(
                "Successfully fetched all contacts",
                count=len(result)
            )
            return result
            
        except Exception as e:
            self._logger.error(
                "Error fetching all contacts",
                exception=e
            )
            raise

    def get_active_contacts(self) -> list[dict]:
        """
        Retrieve only active contacts.
        
        Returns:
            List of active contact dictionaries
        """
        try:
            self._logger.info("Fetching active contacts")
            contacts = self._repository.get_active()
            result = self._serialize_contacts(contacts)
            
            self._logger.info(
                "Successfully fetched active contacts",
                count=len(result)
            )
            return result
            
        except Exception as e:
            self._logger.error(
                "Error fetching active contacts",
                exception=e
            )
            raise

    def get_contact_by_id(self, contact_id: int) -> Optional[dict]:
        """
        Retrieve single contact by ID.
        
        Args:
            contact_id: Primary key of the contact
        
        Returns:
            Contact dictionary or None if not found
        """
        try:
            self._logger.debug(
                "Fetching contact by ID",
                contact_id=contact_id
            )
            
            contact = self._repository.get_by_id(contact_id)
            
            if contact is None:
                self._logger.warning(
                    "Contact not found",
                    contact_id=contact_id
                )
                return None
            
            result = self._serialize_contact(contact)
            self._logger.debug(
                "Successfully fetched contact",
                contact_id=contact_id,
                email=result['email']
            )
            return result
            
        except Exception as e:
            self._logger.error(
                "Error fetching contact by ID",
                exception=e,
                contact_id=contact_id
            )
            raise

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
        # Логируем начало операции
        self._logger.log_operation(
            operation='create_contact',
            status='started',
            email=email,
            name=name
        )
        
        try:
            # Validate input data
            self._validate_contact_data(name, email, phone, status)
            
            # Check email uniqueness
            normalized_email = email.strip().lower()
            if self._repository.exists_by_email(normalized_email):
                self._logger.warning(
                    "Attempt to create contact with duplicate email",
                    email=normalized_email
                )
                raise ValidationError({
                    'email': 'Контакт с таким email уже существует'
                })
            
            # Create contact
            contact = self._repository.create(
                name=name.strip(),
                email=normalized_email,
                phone=phone.strip(),
                status=status
            )
            
            result = self._serialize_contact(contact)
            
            # Логируем успешное создание
            self._logger.log_operation(
                operation='create_contact',
                status='success',
                contact_id=result['id'],
                email=result['email']
            )
            
            return result
            
        except ValidationError as e:
            # Логируем ошибку валидации
            self._logger.log_operation(
                operation='create_contact',
                status='failed',
                email=email
            )
            self._logger.warning(
                "Validation error during contact creation",
                errors=e.message_dict if hasattr(e, 'message_dict') else str(e),
                email=email
            )
            raise
            
        except Exception as e:
            # Логируем неожиданную ошибку
            self._logger.log_operation(
                operation='create_contact',
                status='failed',
                email=email
            )
            self._logger.error(
                "Unexpected error during contact creation",
                exception=e,
                email=email
            )
            raise

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
        # Логируем начало операции
        self._logger.log_operation(
            operation='update_contact',
            status='started',
            contact_id=contact_id,
            email=email
        )
        
        try:
            contact = self._repository.get_by_id(contact_id)
            
            if contact is None:
                self._logger.warning(
                    "Attempt to update non-existent contact",
                    contact_id=contact_id
                )
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
                self._logger.debug(
                    "Checking email uniqueness",
                    contact_id=contact_id,
                    new_email=email,
                    current_email=contact.email.lower(),
                    email_changed=email != contact.email.lower()
                )
                
                if email != contact.email.lower():
                    existing = self._repository.get_by_email(email)
                    
                    self._logger.debug(
                        "Email changed, checking for duplicates",
                        existing_contact_id=existing.id if existing else None,
                        current_contact_id=contact_id
                    )
                    
                    if existing and existing.id != contact_id:
                        self._logger.warning(
                            "Attempt to update contact with duplicate email",
                            contact_id=contact_id,
                            email=email,
                            existing_contact_id=existing.id
                        )
                        raise ValidationError({
                            'email': 'Контакт с таким email уже существует'
                        })
                    
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
            result = self._serialize_contact(updated_contact)
            
            # Логируем успешное обновление
            self._logger.log_operation(
                operation='update_contact',
                status='success',
                contact_id=contact_id,
                updated_fields=list(update_data.keys())
            )
            
            return result
            
        except ValidationError as e:
            # Логируем ошибку валидации
            self._logger.log_operation(
                operation='update_contact',
                status='failed',
                contact_id=contact_id
            )
            self._logger.warning(
                "Validation error during contact update",
                errors=e.message_dict if hasattr(e, 'message_dict') else str(e),
                contact_id=contact_id
            )
            raise
            
        except Exception as e:
            # Логируем неожиданную ошибку
            self._logger.log_operation(
                operation='update_contact',
                status='failed',
                contact_id=contact_id
            )
            self._logger.error(
                "Unexpected error during contact update",
                exception=e,
                contact_id=contact_id
            )
            raise

    def delete_contact(self, contact_id: int) -> bool:
        """
        Delete contact by ID.
        
        Args:
            contact_id: Primary key of the contact
        
        Returns:
            True if deleted, False if not found
        """
        # Логируем начало операции
        self._logger.log_operation(
            operation='delete_contact',
            status='started',
            contact_id=contact_id
        )
        
        try:
            result = self._repository.delete(contact_id)
            
            if result:
                # Логируем успешное удаление
                self._logger.log_operation(
                    operation='delete_contact',
                    status='success',
                    contact_id=contact_id
                )
            else:
                # Контакт не найден
                self._logger.warning(
                    "Attempt to delete non-existent contact",
                    contact_id=contact_id
                )
            
            return result
            
        except Exception as e:
            # Логируем ошибку
            self._logger.log_operation(
                operation='delete_contact',
                status='failed',
                contact_id=contact_id
            )
            self._logger.error(
                "Error during contact deletion",
                exception=e,
                contact_id=contact_id
            )
            raise

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
            self._logger.debug(
                "Contact data validation failed",
                errors=errors
            )
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
