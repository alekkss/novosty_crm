"""
URL configuration for contacts API.
Maps URL patterns to corresponding views (Single Responsibility).
"""

from django.urls import path
from apps.contacts.views import (
    ContactListCreateAPIView,
    ActiveContactsAPIView,
    ContactDetailAPIView,
)

app_name = 'contacts'

urlpatterns = [
    # List all contacts and create new contact
    # GET /api/users - list all contacts
    # POST /api/users - create new contact
    path('users', ContactListCreateAPIView.as_view(), name='contact-list-create'),
    
    # Get only active contacts
    # GET /api/users/active - list active contacts
    path('users/active', ActiveContactsAPIView.as_view(), name='contact-active'),
    
    # Single contact operations
    # GET /api/users/<id> - retrieve contact
    # DELETE /api/users/<id> - delete contact
    path('users/<int:contact_id>', ContactDetailAPIView.as_view(), name='contact-detail'),
]
