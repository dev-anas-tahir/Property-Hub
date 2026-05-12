from django.core.exceptions import PermissionDenied


class HTMXMixin:
    @property
    def is_htmx(self):
        return self.request.headers.get("HX-Request") == "true"


class OwnerRequiredMixin:
    """Raises PermissionDenied if request.user is not the object owner.

    Override get_owner() to return the owner of the object being accessed.
    """

    def get_owner(self):
        raise NotImplementedError("Subclasses must implement get_owner()")

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.user != self.get_owner():
            raise PermissionDenied
        return response
