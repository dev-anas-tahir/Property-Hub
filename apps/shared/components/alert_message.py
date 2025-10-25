from django_unicorn.components import UnicornView


class AlertMessageView(UnicornView):
    """Reusable alert/toast message component for displaying notifications."""
    
    message: str = ""
    message_type: str = "info"  # success, error, warning, info
    show: bool = False
    auto_dismiss: int = 5000  # milliseconds (0 = no auto-dismiss)
    
    def display(self, message: str, message_type: str = "info", auto_dismiss: int = 5000):
        """Display an alert message.
        
        Args:
            message: The message text to display
            message_type: Type of alert (success, error, warning, info)
            auto_dismiss: Time in milliseconds before auto-dismissing (0 = no auto-dismiss)
        """
        self.message = message
        self.message_type = message_type
        self.auto_dismiss = auto_dismiss
        self.show = True
    
    def dismiss(self):
        """Manually dismiss the alert message."""
        self.show = False
        self.message = ""
    
    @property
    def alert_class(self) -> str:
        """Get the Bootstrap alert class based on message type."""
        type_map = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info',
        }
        return type_map.get(self.message_type, 'alert-info')
    
    @property
    def icon_class(self) -> str:
        """Get the icon class based on message type."""
        icon_map = {
            'success': 'bi-check-circle-fill',
            'error': 'bi-exclamation-triangle-fill',
            'warning': 'bi-exclamation-circle-fill',
            'info': 'bi-info-circle-fill',
        }
        return icon_map.get(self.message_type, 'bi-info-circle-fill')
