from django import forms
from apps.properties.models import Property
from apps.properties.validations import validate_cnic, validate_phone


class PropertyForm(forms.ModelForm):
    remove_document = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Remove current document",
    )

    class Meta:
        model = Property
        fields = [
            "name", "description", "full_address", "phone_number",
            "cnic", "property_type", "price", "documents", "is_published"
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
            "documents": forms.FileInput(attrs={"class": "form-control", "accept": ".pdf,application/pdf"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        validate_phone(phone)
        return phone

    def clean_cnic(self):
        cnic = self.cleaned_data.get("cnic")
        validate_cnic(cnic)
        return cnic

    def clean_documents(self):
        documents = self.cleaned_data.get("documents")
        if documents:
            if not documents.name.lower().endswith(".pdf"):
                raise forms.ValidationError("Only PDF files are allowed.")
            if hasattr(documents, "content_type") and documents.content_type != "application/pdf":
                raise forms.ValidationError("File type is not supported. Please upload a PDF file.")
        return documents
