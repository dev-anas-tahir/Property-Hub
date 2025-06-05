from django import forms
from .models import Property


class PropertyForm(forms.ModelForm):
    price = forms.DecimalField()

    class Meta:
        model = Property
        fields = ["name", "description", "full_address", "phone_number", 
        "cnic", "property_type", "price", "documents", "image", "is_published"]
