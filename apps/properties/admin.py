from django.contrib import admin

from apps.properties.models import Property, Favorite


# Register your models here.
admin.site.register(Property)
admin.site.register(Favorite)
