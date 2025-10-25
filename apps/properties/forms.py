"""Forms for property-related operations."""

from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from apps.properties.models import Property, PropertyImage
from apps.properties.validations import validate_phone, validate_cnic


class PropertyForm(forms.ModelForm):
    """Form for creating and editing properties."""
    
    class Meta:
        model = Property
        fields = [
            'name',
            'description',
            'full_address',
            'phone_number',
            'cnic',
            'property_type',
            'price',
            'documents',
            'is_published',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter property name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter property description',
            }),
            'full_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full address',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+92-3001234567',
            }),
            'cnic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345-1234567-1',
            }),
            'property_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter price',
            }),
            'documents': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'name': 'Property Name',
            'description': 'Description',
            'full_address': 'Full Address',
            'phone_number': 'Phone Number',
            'cnic': 'CNIC',
            'property_type': 'Property Type',
            'price': 'Price',
            'documents': 'Documents (PDF)',
            'is_published': 'Publish Property',
        }
        help_texts = {
            'phone_number': 'Format: +92-3001234567',
            'cnic': 'Format: 12345-1234567-1',
            'documents': 'Upload property documents (PDF only)',
            'is_published': 'Make this property visible to other users',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make documents field not required (it's optional)
        self.fields['documents'].required = False
        # Make is_published default to False
        if not self.instance.pk:
            self.fields['is_published'].initial = False
    
    def clean_phone_number(self):
        """Validate phone number using custom validator."""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            try:
                validate_phone(phone)
            except ValidationError as e:
                raise ValidationError(e.message)
        return phone
    
    def clean_cnic(self):
        """Validate CNIC using custom validator."""
        cnic = self.cleaned_data.get('cnic')
        if cnic:
            try:
                validate_cnic(cnic)
            except ValidationError as e:
                raise ValidationError(e.message)
        return cnic
    
    def clean_price(self):
        """Validate that price is a positive decimal."""
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError('Price must be a positive value.')
        return price
    
    def clean_documents(self):
        """Validate that uploaded document is a PDF."""
        document = self.cleaned_data.get('documents')
        if document:
            # Check if it's a new upload (has content_type attribute)
            if hasattr(document, 'content_type'):
                if document.content_type != 'application/pdf':
                    raise ValidationError('Only PDF files are allowed.')
                # Check file size (max 10MB)
                if document.size > 10 * 1024 * 1024:
                    raise ValidationError('File size must not exceed 10MB.')
        return document



class PropertyImageForm(forms.ModelForm):
    """Form for uploading property images."""
    
    class Meta:
        model = PropertyImage
        fields = ['image', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
    
    def clean_image(self):
        """Validate image file type and size."""
        image = self.cleaned_data.get('image')
        if image:
            # Check if it's a new upload (has content_type attribute)
            if hasattr(image, 'content_type'):
                # Validate file type
                valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
                if image.content_type not in valid_types:
                    raise ValidationError('Only image files (JPEG, PNG, GIF, WebP) are allowed.')
                
                # Validate file size (max 5MB)
                if image.size > 5 * 1024 * 1024:
                    raise ValidationError('Image size must not exceed 5MB.')
        return image


# Create inline formset for property images
PropertyImageFormSet = inlineformset_factory(
    Property,
    PropertyImage,
    form=PropertyImageForm,
    extra=5,  # Number of empty forms to display
    max_num=10,  # Maximum number of images allowed
    can_delete=True,  # Allow deletion of existing images
    validate_max=True,  # Validate max_num constraint
)
