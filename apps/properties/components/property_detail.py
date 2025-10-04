"""
Property detail component for displaying comprehensive property information.
"""

from django_unicorn.components import UnicornView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.db import transaction
from apps.properties.models import Property, Favorite
from apps.properties.utils import delete_property_and_assets


class PropertyDetailView(UnicornView):
    """Component for displaying full property details with actions."""
    
    property_id: int = None
    property: Property = None
    is_favorited: bool = False
    is_owner: bool = False
    show_delete_modal: bool = False
    is_loading: bool = False
    
    def mount(self):
        """Initialize component and load property data."""
        if self.property_id:
            self.load_property()
            self.check_ownership()
            self.check_favorite_status()
    
    def load_property(self):
        """Load property with all related data."""
        self.property = get_object_or_404(
            Property.objects.select_related('user')
                           .prefetch_related('images', 'favorited_by'),
            id=self.property_id
        )
    
    def check_ownership(self):
        """Check if the current user owns this property."""
        if self.request.user.is_authenticated and self.property:
            self.is_owner = self.property.user == self.request.user
    
    def check_favorite_status(self):
        """Check if the current user has favorited this property."""
        if self.request.user.is_authenticated and self.property:
            self.is_favorited = Favorite.objects.filter(
                user=self.request.user,
                property=self.property
            ).exists()
    
    def toggle_favorite(self):
        """Toggle the favorite status of the property."""
        if not self.request.user.is_authenticated or not self.property:
            return
        
        self.is_loading = True
        
        try:
            favorite, created = Favorite.objects.get_or_create(
                user=self.request.user,
                property=self.property
            )
            
            if not created:
                # Favorite already existed, so delete it (unfavorite)
                favorite.delete()
                self.is_favorited = False
            else:
                # New favorite was created
                self.is_favorited = True
        finally:
            self.is_loading = False
    
    def show_delete_confirmation(self):
        """Show the delete confirmation modal."""
        if self.is_owner:
            self.show_delete_modal = True
    
    def cancel_delete(self):
        """Cancel the delete action and hide modal."""
        self.show_delete_modal = False
    
    @transaction.atomic
    def delete_property(self):
        """Delete the property and redirect to list."""
        if not self.is_owner or not self.property:
            return
        
        try:
            delete_property_and_assets(self.request, self.property)
            # Redirect to properties list after deletion
            return self.redirect(reverse('properties:list'))
        except Exception as e:
            # Log error and hide modal
            self.show_delete_modal = False
            raise e
