"""
Delete confirmation modal component.
"""

from django_unicorn.components import UnicornView


class DeleteModalView(UnicornView):
    """Component for displaying a delete confirmation modal."""

    show: bool = False
    item_name: str = ""
    item_type: str = "item"

    def show_modal(self, item_name: str = "", item_type: str = "item"):
        """Show the modal with the item details."""
        self.item_name = item_name
        self.item_type = item_type
        self.show = True

    def hide_modal(self):
        """Hide the modal."""
        self.show = False

    def cancel(self):
        """Cancel the delete action and hide modal."""
        self.hide_modal()

    def confirm(self):
        """Confirm the delete action and emit event to parent."""
        self.call("delete_confirmed")
        self.hide_modal()
