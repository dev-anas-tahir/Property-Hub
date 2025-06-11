"""
This module contains forms for property-related operations.
"""

import re
from django import forms
from apps.properties.models import Property
from django.core.exceptions import ValidationError


def validate_cnic(value):
    pattern = r'^\d{5}-\d{7}-\d{1}$'
    if not re.match(pattern, value):
        raise ValidationError('CNIC must be in the format 00000-0000000-0')


def validate_phone(value):
    pattern = r'^\+\d{2}-\d{10}$'
    if not re.match(pattern, value):
        raise ValidationError('Phone number must be in the format +00-0000000000')


class PropertyForm(forms.ModelForm):
    price = forms.DecimalField(
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    remove_document = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Remove current document",
    )

    class Meta:
        model = Property
        fields = [
            "name",
            "description",
            "full_address",
            "phone_number",
            "cnic",
            "property_type",
            "price",
            "documents",
            "is_published",
        ]
        labels = {
            "name": "Property Name",
            "description": "Description",
            "full_address": "Full Address",
            "phone_number": "Phone Number",
            "cnic": "CNIC",
            "property_type": "Property Type",
            "price": "Price",
            "documents": "Document (PDF only)",
            "is_published": "Published",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "full_address": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+92-3001234567"}),
            "cnic": forms.TextInput(attrs={"class": "form-control", "placeholder": "12345-1234567-1"}),
            "property_type": forms.Select(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "documents": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,application/pdf",
                }
            ),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        validators = {
            "phone_number": [validate_phone],
            "cnic": [validate_cnic],
        }

    def clean_documents(self):
        documents = self.cleaned_data.get("documents")
        if documents:  # Only validate if a new file was uploaded
            if not documents.name.lower().endswith(".pdf"):
                raise forms.ValidationError("Only PDF files are allowed.")
            # For newly uploaded files, we can check the content type
            if (
                hasattr(documents, "content_type")
                and documents.content_type != "application/pdf"
            ):
                raise forms.ValidationError(
                    "File type is not supported. Please upload a PDF file."
                )
        return documents
