from django_unicorn.components import UnicornView


class LoadingSpinnerView(UnicornView):
    """Reusable loading spinner component with different styles."""
    
    style: str = "inline"  # inline, overlay, button
    size: str = "md"  # sm, md, lg
    text: str = "Loading..."
    show: bool = True
    color: str = "primary"  # primary, secondary, success, danger, warning, info, light, dark
    
    @property
    def spinner_class(self) -> str:
        """Get the spinner CSS class based on size."""
        size_map = {
            'sm': 'spinner-border-sm',
            'md': '',
            'lg': 'spinner-border-lg',
        }
        size_class = size_map.get(self.size, '')
        return f"spinner-border text-{self.color} {size_class}".strip()
    
    @property
    def container_class(self) -> str:
        """Get the container CSS class based on style."""
        if self.style == "overlay":
            return "position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-dark bg-opacity-50"
        elif self.style == "button":
            return "d-inline-block"
        else:  # inline
            return "d-flex align-items-center justify-content-center my-3"
