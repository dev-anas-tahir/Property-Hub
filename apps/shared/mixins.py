from django.core.exceptions import PermissionDenied


class HTMXMixin:
    @property
    def is_htmx(self):
        return self.request.headers.get("HX-Request") == "true"


class OwnerRequiredMixin:
    owner_field = "user"

    def check_owner(self, obj):
        if getattr(obj, self.owner_field) != self.request.user:
            raise PermissionDenied
