"""Property card component for displaying property summary."""

from django_unicorn.components import UnicornView
from apps.properties.models import Property
from django.shortcuts import get_object_or_404


class PropertyCardView(UnicornView):
    """Component for displaying a property card with summary information."""
    
    property_id: int = None
    property_data: dict = {}
    is_favorited: bool = False
    show_actions: bool = True
    is_owner: bool = False
    
    def mount(self):
        """Initialize component and load property data."""
        if self.property_id:
            self.load_property()
    
    def load_property(self):
        """Load property data with related images and user information."""
        property_obj = get_object_or_404(
            Property.objects.select_related('user').prefetch_related('images'),
            id=self.property_id
        )
        
        # Get the first image or None
        first_image = property_obj.images.first()
        
        # Check if current user is the owner
        if self.request.user.is_authenticated:
            self.is_owner = property_obj.user_id == self.request.user.id
            
            # Check if favorited
            self.is_favorited = property_obj.favorited_by.filter(
                user=self.request.user
            ).exists()
        
        # Build property data dictionary
        self.property_data = {
            'id': property_obj.id,
            'name': property_obj.name,
            'property_type': property_obj.property_type,
            'price': property_obj.price,
            'full_address': property_obj.full_address,
            'description': property_obj.description[:100] + '...' if len(property_obj.description) > 100 else property_obj.description,
            'image_url': first_image.image.url if first_image else None,
            'user_name': property_obj.user.username,
            'created_at': property_obj.created_at,
        }
    
    def property_favorited(self, property_id, is_favorited):
        """Handle favorite toggle event from child component."""
        self.is_favorited = is_favorited
        # Emit event to parent to refresh list if needed
        self.call('refresh_list')
