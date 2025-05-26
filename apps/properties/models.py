from django.db import models


# Create your models here.

class Property(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    image = models.ImageField(upload_to='properties/images/')
    is_published = models.BooleanField(db_default=False)

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"