"""Favorite button component for toggling property favorites."""

from django_unicorn.components import UnicornView
from apps.properties.models import Favorite, Property
from django.shortcuts import get_object_or_404


class FavoriteButtonView(UnicornView):
    """Component for toggling favorite status of a property."""
    
    property_id: int = None
    is_favorited: bool = False
    is_loading: bool = False
    
    def mount(self):
        """Initialize component and check favorite status."""
        if self.property_id and self.request.user.is_authenticated:
            self.check_favorite_status()
    
    def check_favorite_status(self):
        """Check if the current user has favorited this property."""
        self.is_favorited = Favorite.objects.filter(
            user=self.request.user,
            property_id=self.property_id
        ).exists()
    
    def toggle(self):
        """Toggle the favorite status of the property."""
        if not self.request.user.is_authenticated:
            return
        
        self.is_loading = True
        
        try:
            property_obj = get_object_or_404(Property, id=self.property_id)
            favorite, created = Favorite.objects.get_or_create(
                user=self.request.user,
                property=property_obj
            )
            
            if not created:
                # Favorite already existed, so delete it (unfavorite)
                favorite.delete()
                self.is_favorited = False
            else:
                # New favorite was created
                self.is_favorited = True
            
            # Emit event to parent components to refresh their data
            self.call('property_favorited', property_id=self.property_id, is_favorited=self.is_favorited)
            
        finally:
            self.is_loading = False
