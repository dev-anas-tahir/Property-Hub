from django_unicorn.components import UnicornView


class PaginationView(UnicornView):
    """Reusable pagination component for navigating through pages."""
    
    current_page: int = 1
    total_pages: int = 1
    is_loading: bool = False
    
    def next_page(self):
        """Navigate to the next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.call('page_changed', page=self.current_page)
    
    def previous_page(self):
        """Navigate to the previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.call('page_changed', page=self.current_page)
    
    def go_to_page(self, page: int):
        """Navigate to a specific page."""
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self.call('page_changed', page=self.current_page)
    
    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page."""
        return self.current_page > 1
    
    @property
    def has_next(self) -> bool:
        """Check if there is a next page."""
        return self.current_page < self.total_pages
    
    @property
    def page_range(self) -> list:
        """Get a range of page numbers to display."""
        # Show max 5 page numbers at a time
        max_pages = 5
        half = max_pages // 2
        
        if self.total_pages <= max_pages:
            return list(range(1, self.total_pages + 1))
        
        if self.current_page <= half:
            return list(range(1, max_pages + 1))
        
        if self.current_page >= self.total_pages - half:
            return list(range(self.total_pages - max_pages + 1, self.total_pages + 1))
        
        return list(range(self.current_page - half, self.current_page + half + 1))
