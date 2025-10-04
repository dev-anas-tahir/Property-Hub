"""
Property form component for creating and editing properties.
"""

import os
from decimal import Decimal
from django_unicorn.components import UnicornView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.properties.models import Property, PropertyImage
from apps.properties.validations import validate_cnic, validate_phone


class PropertyFormView(UnicornView):
    """Component for handling property creation and editing."""
    
    # Property ID for edit mode
    property_id: int = None
    
    # Form fields
    name: str = ""
    description: str = ""
    full_address: str = ""
    phone_number: str = ""
    cnic: str = ""
    property_type: str = ""
    price: str = ""
    is_published: bool = False
    
    # File handling
    images_to_upload: list = []
    images_preview: list = []
    existing_images: list = []
    images_to_delete: list = []
    document_file = None
    remove_document: bool = False
    current_document_name: str = ""
    
    # Validation errors
    errors: dict = {}
    
    # UI state
    is_loading: bool = False
    is_edit_mode: bool = False
    
    # Property type choices
    property_type_choices = [
        ("", "Select Property Type"),
        ("House", "House"),
        ("Plot", "Plot"),
    ]
    
    def mount(self):
        """Initialize component and load existing property data for edit mode."""
        if self.property_id:
            self.is_edit_mode = True
            self.load_property()
    
    def load_property(self):
        """Load existing property data for editing."""
        try:
            property_obj = get_object_or_404(
                Property.objects.select_related('user').prefetch_related('images'),
                id=self.property_id
            )
            
            # Check ownership
            if property_obj.user != self.request.user:
                raise PermissionError("You don't have permission to edit this property")
            
            # Load property data
            self.name = property_obj.name
            self.description = property_obj.description
            self.full_address = property_obj.full_address
            self.phone_number = property_obj.phone_number
            self.cnic = property_obj.cnic
            self.property_type = property_obj.property_type
            self.price = str(property_obj.price)
            self.is_published = property_obj.is_published
            
            # Load existing images
            self.existing_images = [
                {
                    'id': img.id,
                    'url': img.image.url,
                    'is_primary': img.is_primary
                }
                for img in property_obj.images.all()
            ]
            
            # Load document info
            if property_obj.documents:
                self.current_document_name = os.path.basename(property_obj.documents.name)
        
        except Property.DoesNotExist:
            self.errors['non_field'] = "Property not found"
        except PermissionError as e:
            self.errors['non_field'] = str(e)
    
    def updated_phone_number(self, value):
        """Real-time validation for phone number."""
        if value:
            try:
                validate_phone(value)
                if 'phone_number' in self.errors:
                    del self.errors['phone_number']
            except ValidationError as e:
                self.errors['phone_number'] = str(e.message)
    
    def updated_cnic(self, value):
        """Real-time validation for CNIC."""
        if value:
            try:
                validate_cnic(value)
                if 'cnic' in self.errors:
                    del self.errors['cnic']
            except ValidationError as e:
                self.errors['cnic'] = str(e.message)
    
    def updated_price(self, value):
        """Real-time validation for price."""
        if value:
            try:
                price_decimal = Decimal(value)
                if price_decimal < 0:
                    self.errors['price'] = "Price must be a positive number"
                elif 'price' in self.errors:
                    del self.errors['price']
            except (ValueError, TypeError):
                self.errors['price'] = "Please enter a valid number"
    
    def toggle_image_delete(self, image_id):
        """Toggle an image for deletion."""
        if image_id in self.images_to_delete:
            self.images_to_delete.remove(image_id)
        else:
            self.images_to_delete.append(image_id)
    
    def validate_all(self):
        """Comprehensive validation before save."""
        self.errors = {}
        
        # Required field validation
        if not self.name or not self.name.strip():
            self.errors['name'] = "Property name is required"
        
        if not self.description or not self.description.strip():
            self.errors['description'] = "Description is required"
        
        if not self.full_address or not self.full_address.strip():
            self.errors['full_address'] = "Full address is required"
        
        if not self.phone_number or not self.phone_number.strip():
            self.errors['phone_number'] = "Phone number is required"
        else:
            try:
                validate_phone(self.phone_number)
            except ValidationError as e:
                self.errors['phone_number'] = str(e.message)
        
        if not self.cnic or not self.cnic.strip():
            self.errors['cnic'] = "CNIC is required"
        else:
            try:
                validate_cnic(self.cnic)
            except ValidationError as e:
                self.errors['cnic'] = str(e.message)
        
        if not self.property_type:
            self.errors['property_type'] = "Property type is required"
        
        if not self.price or not self.price.strip():
            self.errors['price'] = "Price is required"
        else:
            try:
                price_decimal = Decimal(self.price)
                if price_decimal < 0:
                    self.errors['price'] = "Price must be a positive number"
            except (ValueError, TypeError):
                self.errors['price'] = "Please enter a valid number"
        
        return len(self.errors) == 0
    
    @transaction.atomic
    def save(self):
        """Save the property with all related data."""
        if not self.validate_all():
            return
        
        self.is_loading = True
        
        try:
            # Get or create property
            if self.is_edit_mode and self.property_id:
                property_obj = get_object_or_404(Property, id=self.property_id)
                
                # Check ownership
                if property_obj.user != self.request.user:
                    self.errors['non_field'] = "You don't have permission to edit this property"
                    self.is_loading = False
                    return
            else:
                property_obj = Property(user=self.request.user)
            
            # Update property fields
            property_obj.name = self.name.strip()
            property_obj.description = self.description.strip()
            property_obj.full_address = self.full_address.strip()
            property_obj.phone_number = self.phone_number.strip()
            property_obj.cnic = self.cnic.strip()
            property_obj.property_type = self.property_type
            property_obj.price = Decimal(self.price)
            property_obj.is_published = self.is_published
            
            # Handle document removal
            if self.remove_document and property_obj.documents:
                property_obj.documents.delete(save=False)
                property_obj.documents = None
            
            property_obj.save()
            
            # Handle image deletion
            if self.images_to_delete:
                for image_id in self.images_to_delete:
                    try:
                        img = PropertyImage.objects.get(id=image_id, property=property_obj)
                        img.image.delete(save=False)
                        img.delete()
                    except PropertyImage.DoesNotExist:
                        continue
            
            # Handle image uploads from request.FILES
            images = self.request.FILES.getlist('images')
            if images:
                self._handle_image_upload(property_obj, images)
            
            # Handle document upload from request.FILES
            document = self.request.FILES.get('documents')
            if document:
                # Validate PDF
                if not document.name.lower().endswith('.pdf'):
                    self.errors['documents'] = "Only PDF files are allowed"
                    self.is_loading = False
                    return
                
                property_obj.documents = document
                property_obj.save(update_fields=['documents'])
            
            self.is_loading = False
            
            # Redirect to detail view
            return self.redirect(reverse('properties:detail', kwargs={'pk': property_obj.pk}))
        
        except Exception as e:
            self.errors['non_field'] = f"An error occurred while saving: {str(e)}"
            self.is_loading = False
    
    def _handle_image_upload(self, property_obj, images):
        """Handle multiple image uploads with validation."""
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        max_size = 5 * 1024 * 1024  # 5MB
        max_files = 10
        
        if len(images) > max_files:
            images = images[:max_files]
        
        valid_images = []
        for img in images:
            if not img or img.size == 0:
                continue
            
            if img.size > max_size:
                continue
            
            ext = os.path.splitext(img.name.lower())[1]
            if ext not in allowed_extensions:
                continue
            
            valid_images.append(PropertyImage(property=property_obj, image=img))
        
        if valid_images:
            PropertyImage.objects.bulk_create(valid_images)
            
            # Set first image as primary if no primary exists
            if not property_obj.images.filter(is_primary=True).exists():
                first_img = property_obj.images.first()
                if first_img:
                    first_img.is_primary = True
                    first_img.save()
