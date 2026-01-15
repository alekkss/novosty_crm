"""
API views for contacts application.
Handles HTTP requests and delegates business logic to services.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from typing import Any

from apps.contacts.serializers import ContactCreateSerializer, ContactListSerializer
from apps.contacts.services import get_contact_service, ContactService


class ContactListCreateAPIView(APIView):
    """
    API View for listing and creating contacts.
    Handles GET and POST requests (Single Responsibility).
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize view with service dependency."""
        super().__init__(**kwargs)
        self._service: ContactService = get_contact_service()
    
    def get(self, request) -> Response:
        """
        GET /api/users
        Retrieve all contacts.
        
        Returns:
            Response with list of contacts in format:
            {
                "users": [
                    {"id": 1, "name": "...", "email": "...", "phone": "...", "status": "active"},
                    ...
                ]
            }
        """
        try:
            # Get all contacts from service
            contacts = self._service.get_all_contacts()
            
            # Return response in format expected by frontend
            return Response(
                {'users': contacts},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'error': f'Ошибка при получении контактов: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request) -> Response:
        """
        POST /api/users
        Create new contact.
        
        Request body:
            {
                "name": "Иван Иванов",
                "email": "ivan@example.com",
                "phone": "+7 900 123-45-67",
                "status": "active"  // optional, default: "active"
            }
        
        Returns:
            Response with created contact or validation errors
        """
        # Validate input data
        serializer = ContactCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create contact through service
            validated_data = serializer.validated_data
            contact = self._service.create_contact(
                name=validated_data['name'],
                email=validated_data['email'],
                phone=validated_data['phone'],
                status=validated_data.get('status', 'active')
            )
            
            return Response(
                {
                    'message': 'Контакт успешно создан',
                    'contact': contact
                },
                status=status.HTTP_201_CREATED
            )
        
        except ValidationError as e:
            # Handle business logic validation errors
            error_message = e.message_dict if hasattr(e, 'message_dict') else str(e)
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Handle unexpected errors
            return Response(
                {'error': f'Ошибка при создании контакта: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ActiveContactsAPIView(APIView):
    """
    API View for retrieving only active contacts.
    Demonstrates Open/Closed Principle - new endpoint without modifying existing.
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize view with service dependency."""
        super().__init__(**kwargs)
        self._service: ContactService = get_contact_service()
    
    def get(self, request) -> Response:
        """
        GET /api/users/active
        Retrieve only active contacts.
        
        Returns:
            Response with list of active contacts
        """
        try:
            contacts = self._service.get_active_contacts()
            
            return Response(
                {'users': contacts},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'error': f'Ошибка при получении активных контактов: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ContactDetailAPIView(APIView):
    """
    API View for retrieving, updating and deleting single contact.
    Handles GET, PUT, PATCH, DELETE requests for specific contact.
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize view with service dependency."""
        super().__init__(**kwargs)
        self._service: ContactService = get_contact_service()
    
    def get(self, request, contact_id: int) -> Response:
        """
        GET /api/users/<id>
        Retrieve single contact by ID.
        """
        contact = self._service.get_contact_by_id(contact_id)
        
        if contact is None:
            return Response(
                {'error': 'Контакт не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(contact, status=status.HTTP_200_OK)
    
    def delete(self, request, contact_id: int) -> Response:
        """
        DELETE /api/users/<id>
        Delete contact by ID.
        """
        deleted = self._service.delete_contact(contact_id)
        
        if not deleted:
            return Response(
                {'error': 'Контакт не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {'message': 'Контакт успешно удален'},
            status=status.HTTP_200_OK
        )
