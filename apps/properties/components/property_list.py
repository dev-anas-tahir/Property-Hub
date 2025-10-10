"""Property list component with pagination and filtering."""

import logging

from django_unicorn.components import UnicornView
from django.core.paginator import Paginator

from apps.properties.models import Property

logger = logging.getLogger(__name__)


class PropertyListView(UnicornView):
    """Component for displaying a paginated list of properties with filtering."""

    # Pagination
    current_page: int = 1
    per_page: int = 9
    total_pages: int = 1
    total_count: int = 0

    # Filters
    show_favorites_only: bool = False
    show_my_properties: bool = False

    # Data
    properties: list = []

    # State
    is_loading: bool = False

    def mount(self):
        """Initialize component and load initial properties."""
        self.load_properties()

    def load_properties(self):
        """Load properties based on current filters and pagination."""
        self.is_loading = True

        # Build base queryset
        queryset = Property.objects.select_related("user").prefetch_related("images")

        # Apply filters
        if self.show_favorites_only and self.request.user.is_authenticated:
            queryset = queryset.filter(favorited_by__user=self.request.user).distinct()

        if self.show_my_properties and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)

        # Get total count
        self.total_count = queryset.count()

        # Apply pagination
        paginator = Paginator(queryset, self.per_page)
        self.total_pages = paginator.num_pages

        # Ensure current page is valid
        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages
        elif self.current_page < 1:
            self.current_page = 1

        # Get page data
        page_obj = paginator.get_page(self.current_page)

        # Convert properties to list of IDs for property cards
        self.properties = [prop.id for prop in page_obj.object_list]

        self.is_loading = False

    def page_changed(self, page: int):
        """Handle page change event from pagination component."""
        self.current_page = page
        self.load_properties()

    def next_page(self):
        """Navigate to the next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_properties()

    def previous_page(self):
        """Navigate to the previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_properties()

    def go_to_page(self, page: int):
        """Navigate to a specific page."""
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self.load_properties()

    def refresh_list(self):
        """Refresh the property list (called when favorites are toggled)."""
        self.load_properties()

    def property_favorited(self, property_id: int, is_favorited: bool):
        logger.warning(
            f"property_list.py property_favorited called with property_id={property_id}, is_favorited={is_favorited}"
        )
        # If showing favorites only and property was unfavorited, refresh list
        if self.show_favorites_only and not is_favorited:
            self.load_properties()

    @property
    def has_properties(self) -> bool:
        """Check if there are any properties to display."""
        return len(self.properties) > 0

    @property
    def empty_message(self) -> str:
        """Get appropriate empty state message based on filters."""
        if self.show_favorites_only:
            return "You have no favorite properties yet. Start exploring and add some favorites!"
        elif self.show_my_properties:
            return "You haven't created any properties yet. Create your first property to get started!"
        else:
            return "No properties available at the moment."
