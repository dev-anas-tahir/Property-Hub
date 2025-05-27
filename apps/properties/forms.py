from django import forms
from .models import Property


class PropertyForm(forms.ModelForm):
    price = forms.DecimalField(min_value=0)

    class Meta:
        model = Property
        fields = ["name", "description", "address", "price", "image", "is_published"]
