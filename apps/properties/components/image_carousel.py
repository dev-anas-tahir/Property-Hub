"""
Image carousel component for displaying property images.
"""

from django_unicorn.components import UnicornView
from apps.properties.models import PropertyImage


class ImageCarouselView(UnicornView):
    """Component for displaying property images in an interactive carousel."""

    property_id: int = None
    images: list = []
    current_index: int = 0

    def mount(self):
        """Load images when component mounts."""
        if self.property_id:
            self.load_images()

    def load_images(self):
        """Load all images for the property."""
        image_objects = PropertyImage.objects.filter(
            property_id=self.property_id
        ).order_by("-is_primary", "uploaded_at")

        self.images = [
            {"id": img.id, "url": img.image.url, "is_primary": img.is_primary}
            for img in image_objects
        ]

    def next_image(self):
        """Navigate to the next image."""
        if self.images:
            self.current_index = (self.current_index + 1) % len(self.images)

    def previous_image(self):
        """Navigate to the previous image."""
        if self.images:
            self.current_index = (self.current_index - 1) % len(self.images)

    def go_to_image(self, index: int):
        """Navigate to a specific image by index."""
        if 0 <= index < len(self.images):
            self.current_index = index

    def handle_keydown(self, key: str):
        """Handle keyboard navigation."""
        if key == "ArrowRight":
            self.next_image()
        elif key == "ArrowLeft":
            self.previous_image()
