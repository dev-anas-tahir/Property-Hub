from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.properties.models import Property, Favorite, PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    readonly_fields = ('preview_image',)
    fields = ('image', 'preview_image', 'is_primary')
    
    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px;" />')
        return "No image"
    preview_image.short_description = 'Preview'


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'property_type', 'price', 'user', 'created_at', 'is_published')
    list_filter = ('property_type', 'is_published', 'created_at')
    search_fields = ('name', 'description', 'full_address')
    inlines = [PropertyImageInline]
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set user during the first save.
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'property_link', 'is_primary', 'uploaded_at')
    list_filter = ('is_primary', 'uploaded_at')
    list_editable = ('is_primary',)
    search_fields = ('property__name',)
    readonly_fields = ('preview_image',)
    
    def property_link(self, obj):
        url = reverse('admin:properties_property_change', args=[obj.property.id])
        return format_html('<a href="{}">{}</a>', url, obj.property.name)
    property_link.short_description = 'Property'
    property_link.admin_order_field = 'property__name'
    
    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 200px;" />')
        return "No image"
    preview_image.short_description = 'Preview'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'favorited_at')
    list_filter = ('favorited_at',)
    search_fields = ('user__username', 'property__name')
    date_hierarchy = 'favorited_at'
