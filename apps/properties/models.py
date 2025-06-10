from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Property(models.Model):
    class PropertyType(models.TextChoices):
        HOUSE = "House"
        PLOT = "Plot"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    full_address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    cnic = models.CharField(max_length=13)
    property_type = models.CharField(max_length=10, choices=PropertyType.choices)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=0, validators=[MinValueValidator(0)])
    documents = models.FileField(upload_to='properties/documents/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ["-created_at"]


def property_image_upload_path(instance, filename):
    """Generate upload path for property images"""
    return f'properties/images/{instance.property.id}/{filename}'


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=property_image_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(default=False, help_text="Mark as primary image")

    def __str__(self):
        return f"Image for {self.property.name}"

    class Meta:
        ordering = ['-is_primary', 'uploaded_at']
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'

    def save(self, *args, **kwargs):
        # If this is set as primary, unset any other primary images for this property
        if self.is_primary:
            PropertyImage.objects.filter(
                property=self.property, 
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    favorited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')  # prevents duplicates
        ordering = ["-favorited_at"]

    def __str__(self):
        return f"{self.user.username} favorited {self.property.name}"