"""
Test cases for property-related Unicorn components.
"""

import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from apps.properties.models import Property, PropertyImage, Favorite
from apps.properties.components.property_list import PropertyListView
from apps.properties.components.property_card import PropertyCardView
from apps.properties.components.favorite_button import FavoriteButtonView
from apps.properties.components.property_detail import PropertyDetailView
from apps.properties.components.property_form import PropertyFormView
from apps.properties.components.image_carousel import ImageCarouselView
from apps.properties.components.delete_modal import DeleteModalView
from decimal import Decimal


@pytest.fixture
def request_factory():
    """Fixture for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def authenticated_request(request_factory, user):
    """Fixture for creating an authenticated request."""
    request = request_factory.get('/')
    request.user = user
    return request


@pytest.fixture
def anonymous_request(request_factory):
    """Fixture for creating an anonymous request."""
    request = request_factory.get('/')
    request.user = AnonymousUser()
    return request


@pytest.fixture
def property_factory(user):
    """Fixture for creating test properties."""
    def create_property(**kwargs):
        defaults = {
            'user': user,
            'name': 'Test Property',
            'description': 'Test description',
            'full_address': 'Test address',
            'phone_number': '+92-3001234567',
            'cnic': '12345-1234567-1',
            'property_type': 'House',
            'price': Decimal('100000'),
            'is_published': True,
        }
        defaults.update(kwargs)
        return Property.objects.create(**defaults)
    return create_property


@pytest.fixture
def multiple_properties(property_factory, user):
    """Fixture for creating multiple test properties."""
    properties = []
    for i in range(15):
        prop = property_factory(
            name=f'Property {i+1}',
            price=Decimal(str(100000 + i * 10000))
        )
        properties.append(prop)
    return properties


# ============================================================================
# Task 10.1: Test property listing and filtering
# ============================================================================

@pytest.mark.django_db
class TestPropertyListComponent:
    """Tests for PropertyListView component."""
    
    def test_property_list_loads_correctly(self, authenticated_request, multiple_properties):
        """Test that property list component loads correctly with properties."""
        component = PropertyListView(
            component_id='test',
            component_name='property-list',
            request=authenticated_request
        )
        component.mount()
        
        # Should load first page with 9 properties
        assert len(component.properties) == 9
        assert component.current_page == 1
        assert component.total_pages == 2  # 15 properties / 9 per page = 2 pages
        assert component.total_count == 15
        assert component.has_properties is True
    
    def test_property_list_empty_state(self, authenticated_request):
        """Test that empty state displays correctly when no properties exist."""
        component = PropertyListView(
            component_id='test',
            component_name='property-list',
            request=authenticated_request
        )
        component.mount()
        
        assert len(component.properties) == 0
        assert component.has_properties is False
        assert component.empty_message == "No properties available at the moment."
    
    def test_pagination_next_page(self, authenticated_request, multiple_properties):
        """Test pagination next page functionality."""
        component = PropertyListView(
            component_id='test',
            component_name='property-list',
            request=authenticated_request
        )
        component.mount()
        
        # Navigate to next page
        component.next_page()
        
        assert component.current_page == 2
        assert len(component.properties) == 6  # Remaining properties
    
    def test_pagination_previous_page(self, authenticated_request, multiple_properties):
        """Test pagination previous page functionality."""
        component = PropertyListView(
            component_id='test',
            component_name='property-list',
            request=authenticated_request
        )
        component.mount()
        component.current_page = 2
        component.load_properties()
        
        # Navigate to previous page
        component.previous_page()
        
        assert component.current_page == 1
        assert len(component.properties) == 9
    
    def test_pagination_go_to_page(self, authenticated_request, multiple_properties):
        """Test pagination go to specific page functionality."""
        component = PropertyListView(
            component_id='test',
            component_name='property-list',
            request=authenticated_request
        )
        component.mount()
        
        # Go to page 2
        component.go_to_page(2)
        
        assert component.current_page == 2
        assert len(component.properties) == 6
    
    def test_pagination_boundary_conditions(self, authenticated_request, multiple_properties):
        """Test pagination doesn't go beyond boundaries."""
        component = PropertyListView(
            component_id='test',
            component_name='property-list',
            request=authenticated_request
        )
        component.mount()
        
        # Try to go to page 0
        component.go_to_page(0)
        assert component.current_page == 1
        
        # Try to go beyond last page
        component.go_to_page(999)
        assert component.current_page == 1  # Should stay on current page
    
    def test_favorites_filter_shows_only_favorited(self, authenticated_request, multiple_properties):
        """Test that favorites filter shows only favorited properties."""
        user = authenticated_request.user
        
        # Favorite first 3 properties
        for prop in multiple_properties[:3]:
            Favorite.objects.create(user=user, property=prop)
        
        component = PropertyListView(
            component_id='test',
            component_name='property-list',
            request=authenticated_request
        )
        component.show_favorites_only = True
        component.mount()
        
        assert len(component.properties) == 3
        assert component.total_count == 3
        assert component.has_properties is True
    
    def test_favorites_filter_empty_state(self, authenticated_request, multiple_properties):
        """Test favorites filter empty state when no favorites exist."""
        component = PropertyListView(
            component_id='test',
            component_name='property-list',
            request=authenticated_request
        )
        component.show_favorites_only = True
        component.mount()
        
        assert len(component.properties) == 0
        assert component.has_properties is False
        assert "no favorite properties" in component.empty_message.lower()
    
    def test_my_properties_filter_shows_only_user_properties(self, authenticated_request, property_factory):
        """Test that my properties filter shows only user's properties."""
        user = authenticated_request.user
        
        # Create properties for current user
        for i in range(5):
            property_factory(user=user, name=f'My Property {i+1}')
        
        # Create properties for another user
        other_user = User.objects.create_user(username='other', password='pass')
        for i in range(3):
            property_factory(user=other_user, name=f'Other Property {i+1}')
        
        component = PropertyListView(
            component_id='test',
            component_name='property-list',
            request=authenticated_request
        )
        component.show_my_properties = True
        component.mount()
        
        assert len(component.properties) == 5
        assert component.total_count == 5
    
    def test_my_properties_filter_empty_state(self, authenticated_request):
        """Test my properties filter empty state when user has no properties."""
        component = PropertyListView(
            component_id='test',
            component_name='property-list',
            request=authenticated_request
        )
        component.show_my_properties = True
        component.mount()
        
        assert len(component.properties) == 0
        assert component.has_properties is False
        assert "haven't created any properties" in component.empty_message.lower()
    
    def test_favorite_toggle_updates_list(self, authenticated_request, multiple_properties):
        """Test that favorite toggle updates the list when showing favorites only."""
        user = authenticated_request.user
        
        # Favorite first 3 properties
        favorites = []
        for prop in multiple_properties[:3]:
            fav = Favorite.objects.create(user=user, property=prop)
            favorites.append(fav)
        
        component = PropertyListView(
            component_id='test',
            component_name='property-list',
            request=authenticated_request
        )
        component.show_favorites_only = True
        component.mount()
        
        initial_count = len(component.properties)
        assert initial_count == 3
        
        # Actually remove the favorite from database (simulating what favorite button does)
        favorites[0].delete()
        
        # Simulate unfavoriting a property event
        component.property_favorited(multiple_properties[0].id, False)
        
        # List should refresh and show one less property
        assert len(component.properties) == 2


@pytest.mark.django_db
class TestPropertyCardComponent:
    """Tests for PropertyCardView component."""
    
    def test_property_card_loads_data(self, authenticated_request, property_factory):
        """Test that property card loads property data correctly."""
        prop = property_factory(name='Test House', price=Decimal('250000'))
        
        component = PropertyCardView(
            component_id='test',
            component_name='property-card',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert component.property_data['name'] == 'Test House'
        assert component.property_data['price'] == Decimal('250000')
        assert component.property_data['id'] == prop.id
    
    def test_property_card_shows_owner_status(self, authenticated_request, property_factory):
        """Test that property card correctly identifies owner."""
        user = authenticated_request.user
        prop = property_factory(user=user)
        
        component = PropertyCardView(
            component_id='test',
            component_name='property-card',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert component.is_owner is True
    
    def test_property_card_shows_favorite_status(self, authenticated_request, property_factory):
        """Test that property card shows correct favorite status."""
        user = authenticated_request.user
        prop = property_factory()
        Favorite.objects.create(user=user, property=prop)
        
        component = PropertyCardView(
            component_id='test',
            component_name='property-card',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert component.is_favorited is True


@pytest.mark.django_db
class TestFavoriteButtonComponent:
    """Tests for FavoriteButtonView component."""
    
    def test_favorite_button_checks_status(self, authenticated_request, property_factory):
        """Test that favorite button checks favorite status correctly."""
        user = authenticated_request.user
        prop = property_factory()
        Favorite.objects.create(user=user, property=prop)
        
        component = FavoriteButtonView(
            component_id='test',
            component_name='favorite-button',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert component.is_favorited is True
    
    def test_favorite_button_toggle_adds_favorite(self, authenticated_request, property_factory, monkeypatch):
        """Test that toggle adds a favorite when not favorited."""
        user = authenticated_request.user
        prop = property_factory()
        
        # Mock the call method to avoid TypeError in tests
        def mock_call(*args, **kwargs):
            pass
        
        component = FavoriteButtonView(
            component_id='test',
            component_name='favorite-button',
            request=authenticated_request
        )
        monkeypatch.setattr(component, 'call', mock_call)
        component.property_id = prop.id
        component.mount()
        
        assert component.is_favorited is False
        
        # Toggle to favorite
        component.toggle()
        
        assert component.is_favorited is True
        assert Favorite.objects.filter(user=user, property=prop).exists()
    
    def test_favorite_button_toggle_removes_favorite(self, authenticated_request, property_factory, monkeypatch):
        """Test that toggle removes a favorite when already favorited."""
        user = authenticated_request.user
        prop = property_factory()
        Favorite.objects.create(user=user, property=prop)
        
        # Mock the call method to avoid TypeError in tests
        def mock_call(*args, **kwargs):
            pass
        
        component = FavoriteButtonView(
            component_id='test',
            component_name='favorite-button',
            request=authenticated_request
        )
        monkeypatch.setattr(component, 'call', mock_call)
        component.property_id = prop.id
        component.mount()
        
        assert component.is_favorited is True
        
        # Toggle to unfavorite
        component.toggle()
        
        assert component.is_favorited is False
        assert not Favorite.objects.filter(user=user, property=prop).exists()
    
    def test_favorite_button_requires_authentication(self, anonymous_request, property_factory):
        """Test that favorite button doesn't work for anonymous users."""
        prop = property_factory()
        
        component = FavoriteButtonView(
            component_id='test',
            component_name='favorite-button',
            request=anonymous_request
        )
        component.property_id = prop.id
        component.mount()
        
        # Try to toggle (should do nothing)
        component.toggle()
        
        assert component.is_favorited is False
        assert Favorite.objects.count() == 0



# ============================================================================
# Task 10.2: Test property detail and actions
# ============================================================================

@pytest.mark.django_db
class TestPropertyDetailComponent:
    """Tests for PropertyDetailView component."""
    
    def test_property_detail_loads_all_data(self, authenticated_request, property_factory):
        """Test that property detail component loads all data correctly."""
        prop = property_factory(
            name='Luxury Villa',
            description='Beautiful villa with ocean view',
            price=Decimal('500000')
        )
        
        component = PropertyDetailView(
            component_id='test',
            component_name='property-detail',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert component.property is not None
        assert component.property.name == 'Luxury Villa'
        assert component.property.price == Decimal('500000')
    
    def test_property_detail_checks_ownership(self, authenticated_request, property_factory):
        """Test that property detail correctly identifies owner."""
        user = authenticated_request.user
        prop = property_factory(user=user)
        
        component = PropertyDetailView(
            component_id='test',
            component_name='property-detail',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert component.is_owner is True
    
    def test_property_detail_non_owner(self, authenticated_request, property_factory):
        """Test that property detail correctly identifies non-owner."""
        other_user = User.objects.create_user(username='other', password='pass')
        prop = property_factory(user=other_user)
        
        component = PropertyDetailView(
            component_id='test',
            component_name='property-detail',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert component.is_owner is False
    
    def test_property_detail_favorite_status(self, authenticated_request, property_factory):
        """Test that property detail shows correct favorite status."""
        user = authenticated_request.user
        prop = property_factory()
        Favorite.objects.create(user=user, property=prop)
        
        component = PropertyDetailView(
            component_id='test',
            component_name='property-detail',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert component.is_favorited is True
    
    def test_property_detail_toggle_favorite(self, authenticated_request, property_factory):
        """Test favorite toggle works from detail page."""
        user = authenticated_request.user
        prop = property_factory()
        
        component = PropertyDetailView(
            component_id='test',
            component_name='property-detail',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert component.is_favorited is False
        
        # Toggle to favorite
        component.toggle_favorite()
        
        assert component.is_favorited is True
        assert Favorite.objects.filter(user=user, property=prop).exists()
        
        # Toggle to unfavorite
        component.toggle_favorite()
        
        assert component.is_favorited is False
        assert not Favorite.objects.filter(user=user, property=prop).exists()
    
    def test_delete_modal_shows(self, authenticated_request, property_factory):
        """Test that delete modal shows correctly."""
        user = authenticated_request.user
        prop = property_factory(user=user)
        
        component = PropertyDetailView(
            component_id='test',
            component_name='property-detail',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert component.show_delete_modal is False
        
        # Show delete modal
        component.show_delete_confirmation()
        
        assert component.show_delete_modal is True
    
    def test_delete_modal_cancels(self, authenticated_request, property_factory):
        """Test that delete modal cancels correctly."""
        user = authenticated_request.user
        prop = property_factory(user=user)
        
        component = PropertyDetailView(
            component_id='test',
            component_name='property-detail',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        # Show and then cancel
        component.show_delete_confirmation()
        assert component.show_delete_modal is True
        
        component.cancel_delete()
        assert component.show_delete_modal is False
    
    def test_delete_property_removes_and_redirects(self, authenticated_request, property_factory, monkeypatch):
        """Test that delete functionality removes property."""
        import apps.properties.components.property_detail as detail_module
        
        # Mock delete_property_and_assets to avoid messages middleware requirement
        def mock_delete(request, property_obj):
            property_obj.delete()
        
        monkeypatch.setattr(detail_module, 'delete_property_and_assets', mock_delete)
        
        user = authenticated_request.user
        prop = property_factory(user=user)
        property_id = prop.id
        
        component = PropertyDetailView(
            component_id='test',
            component_name='property-detail',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        # Delete property
        result = component.delete_property()
        
        # Should redirect
        assert result is not None
        
        # Property should be deleted
        assert not Property.objects.filter(id=property_id).exists()
    
    def test_delete_property_requires_ownership(self, authenticated_request, property_factory):
        """Test that ownership checks prevent unauthorized deletes."""
        other_user = User.objects.create_user(username='other', password='pass')
        prop = property_factory(user=other_user)
        property_id = prop.id
        
        component = PropertyDetailView(
            component_id='test',
            component_name='property-detail',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        # Try to delete (should not work)
        component.delete_property()
        
        # Property should still exist
        assert Property.objects.filter(id=property_id).exists()
    
    def test_anonymous_user_cannot_favorite(self, anonymous_request, property_factory):
        """Test that anonymous users cannot favorite properties."""
        prop = property_factory()
        
        component = PropertyDetailView(
            component_id='test',
            component_name='property-detail',
            request=anonymous_request
        )
        component.property_id = prop.id
        component.mount()
        
        # Try to toggle favorite (should do nothing)
        component.toggle_favorite()
        
        assert component.is_favorited is False
        assert Favorite.objects.count() == 0


@pytest.mark.django_db
class TestImageCarouselComponent:
    """Tests for ImageCarouselView component."""
    
    def test_image_carousel_loads_images(self, authenticated_request, property_factory):
        """Test that image carousel loads images correctly."""
        prop = property_factory()
        
        # Create some images
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io
        
        for i in range(3):
            # Create a simple test image
            img = Image.new('RGB', (100, 100), color='red')
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG')
            img_io.seek(0)
            
            PropertyImage.objects.create(
                property=prop,
                image=SimpleUploadedFile(f'test{i}.jpg', img_io.read(), content_type='image/jpeg')
            )
        
        component = ImageCarouselView(
            component_id='test',
            component_name='image-carousel',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert len(component.images) == 3
        assert component.current_index == 0
    
    def test_image_carousel_navigation_next(self, authenticated_request, property_factory):
        """Test image carousel next navigation."""
        prop = property_factory()
        
        # Create test images
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io
        
        for i in range(3):
            img = Image.new('RGB', (100, 100), color='red')
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG')
            img_io.seek(0)
            
            PropertyImage.objects.create(
                property=prop,
                image=SimpleUploadedFile(f'test{i}.jpg', img_io.read(), content_type='image/jpeg')
            )
        
        component = ImageCarouselView(
            component_id='test',
            component_name='image-carousel',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert component.current_index == 0
        
        # Navigate next
        component.next_image()
        assert component.current_index == 1
        
        component.next_image()
        assert component.current_index == 2
        
        # Should wrap around
        component.next_image()
        assert component.current_index == 0
    
    def test_image_carousel_navigation_previous(self, authenticated_request, property_factory):
        """Test image carousel previous navigation."""
        prop = property_factory()
        
        # Create test images
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io
        
        for i in range(3):
            img = Image.new('RGB', (100, 100), color='red')
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG')
            img_io.seek(0)
            
            PropertyImage.objects.create(
                property=prop,
                image=SimpleUploadedFile(f'test{i}.jpg', img_io.read(), content_type='image/jpeg')
            )
        
        component = ImageCarouselView(
            component_id='test',
            component_name='image-carousel',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        # Navigate previous (should wrap to last)
        component.previous_image()
        assert component.current_index == 2
        
        component.previous_image()
        assert component.current_index == 1
    
    def test_image_carousel_go_to_image(self, authenticated_request, property_factory):
        """Test image carousel go to specific image."""
        prop = property_factory()
        
        # Create test images
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io
        
        for i in range(3):
            img = Image.new('RGB', (100, 100), color='red')
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG')
            img_io.seek(0)
            
            PropertyImage.objects.create(
                property=prop,
                image=SimpleUploadedFile(f'test{i}.jpg', img_io.read(), content_type='image/jpeg')
            )
        
        component = ImageCarouselView(
            component_id='test',
            component_name='image-carousel',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        # Go to specific image
        component.go_to_image(2)
        assert component.current_index == 2
        
        # Invalid index should not change
        component.go_to_image(10)
        assert component.current_index == 2
    
    def test_image_carousel_empty_state(self, authenticated_request, property_factory):
        """Test image carousel handles empty state when no images exist."""
        prop = property_factory()
        
        component = ImageCarouselView(
            component_id='test',
            component_name='image-carousel',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert len(component.images) == 0
        
        # Navigation should not crash with no images
        component.next_image()
        component.previous_image()


@pytest.mark.django_db
class TestDeleteModalComponent:
    """Tests for DeleteModalView component."""
    
    def test_delete_modal_shows(self, authenticated_request):
        """Test that delete modal shows correctly."""
        component = DeleteModalView(
            component_id='test',
            component_name='delete-modal',
            request=authenticated_request
        )
        
        assert component.show is False
        
        component.show_modal(item_name='Test Property', item_type='property')
        
        assert component.show is True
        assert component.item_name == 'Test Property'
        assert component.item_type == 'property'
    
    def test_delete_modal_hides(self, authenticated_request):
        """Test that delete modal hides correctly."""
        component = DeleteModalView(
            component_id='test',
            component_name='delete-modal',
            request=authenticated_request
        )
        
        component.show_modal(item_name='Test Property')
        assert component.show is True
        
        component.hide_modal()
        assert component.show is False
    
    def test_delete_modal_cancel(self, authenticated_request):
        """Test that delete modal cancel works."""
        component = DeleteModalView(
            component_id='test',
            component_name='delete-modal',
            request=authenticated_request
        )
        
        component.show_modal(item_name='Test Property')
        assert component.show is True
        
        component.cancel()
        assert component.show is False
    
    def test_delete_modal_confirm(self, authenticated_request, monkeypatch):
        """Test that delete modal confirm emits event."""
        # Mock the call method
        call_args = []
        def mock_call(*args, **kwargs):
            call_args.append((args, kwargs))
        
        component = DeleteModalView(
            component_id='test',
            component_name='delete-modal',
            request=authenticated_request
        )
        monkeypatch.setattr(component, 'call', mock_call)
        
        component.show_modal(item_name='Test Property')
        component.confirm()
        
        # Should have called delete_confirmed
        assert len(call_args) > 0
        assert component.show is False



# ============================================================================
# Task 10.3: Test property forms
# ============================================================================

@pytest.mark.django_db
class TestPropertyFormComponent:
    """Tests for PropertyFormView component."""
    
    def test_create_form_displays_empty_fields(self, authenticated_request):
        """Test that create form displays empty fields."""
        component = PropertyFormView(
            component_id='test',
            component_name='property-form',
            request=authenticated_request
        )
        component.mount()
        
        assert component.name == ""
        assert component.description == ""
        assert component.full_address == ""
        assert component.phone_number == ""
        assert component.cnic == ""
        assert component.property_type == ""
        assert component.price == ""
        assert component.is_published is False
        assert component.is_edit_mode is False
    
    def test_edit_form_prepopulates_with_existing_data(self, authenticated_request, property_factory):
        """Test that edit form pre-populates with existing data."""
        user = authenticated_request.user
        prop = property_factory(
            user=user,
            name='Test Villa',
            description='Beautiful villa',
            full_address='123 Main St',
            phone_number='+92-3001234567',
            cnic='12345-1234567-1',
            property_type='House',
            price=Decimal('500000'),
            is_published=True
        )
        
        component = PropertyFormView(
            component_id='test',
            component_name='property-form',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        assert component.name == 'Test Villa'
        assert component.description == 'Beautiful villa'
        assert component.full_address == '123 Main St'
        assert component.phone_number == '+92-3001234567'
        assert component.cnic == '12345-1234567-1'
        assert component.property_type == 'House'
        assert component.price == '500000'
        assert component.is_published is True
        assert component.is_edit_mode is True
    
    def test_real_time_phone_validation(self, authenticated_request):
        """Test that real-time validation shows errors immediately for phone."""
        component = PropertyFormView(
            component_id='test',
            component_name='property-form',
            request=authenticated_request
        )
        component.mount()
        
        # Invalid phone number
        component.updated_phone_number('invalid')
        assert 'phone_number' in component.errors
        
        # Valid phone number
        component.updated_phone_number('+92-3001234567')
        assert 'phone_number' not in component.errors
    
    def test_real_time_cnic_validation(self, authenticated_request):
        """Test that real-time validation shows errors immediately for CNIC."""
        component = PropertyFormView(
            component_id='test',
            component_name='property-form',
            request=authenticated_request
        )
        component.mount()
        
        # Invalid CNIC
        component.updated_cnic('invalid')
        assert 'cnic' in component.errors
        
        # Valid CNIC
        component.updated_cnic('12345-1234567-1')
        assert 'cnic' not in component.errors
    
    def test_real_time_price_validation(self, authenticated_request):
        """Test that real-time validation shows errors immediately for price."""
        component = PropertyFormView(
            component_id='test',
            component_name='property-form',
            request=authenticated_request
        )
        component.mount()
        
        # Invalid price (negative)
        component.updated_price('-100')
        assert 'price' in component.errors
        
        # Valid price
        component.updated_price('100000')
        assert 'price' not in component.errors
    
    def test_form_validation_prevents_invalid_submission(self, authenticated_request):
        """Test that validation prevents invalid data submission."""
        component = PropertyFormView(
            component_id='test',
            component_name='property-form',
            request=authenticated_request
        )
        component.mount()
        
        # Try to validate with empty fields
        is_valid = component.validate_all()
        
        assert is_valid is False
        assert 'name' in component.errors
        assert 'description' in component.errors
        assert 'full_address' in component.errors
        assert 'phone_number' in component.errors
        assert 'cnic' in component.errors
        assert 'property_type' in component.errors
        assert 'price' in component.errors
    
    def test_form_submission_saves_data_correctly(self, authenticated_request, monkeypatch):
        """Test that form submission saves data correctly."""
        # Mock request.FILES methods
        monkeypatch.setattr(authenticated_request.FILES, 'getlist', lambda x: [])
        monkeypatch.setattr(authenticated_request.FILES, 'get', lambda x: None)
        
        component = PropertyFormView(
            component_id='test',
            component_name='property-form',
            request=authenticated_request
        )
        component.mount()
        
        # Fill in valid data
        component.name = 'New Property'
        component.description = 'A beautiful new property'
        component.full_address = '456 Oak Ave'
        component.phone_number = '+92-3001234567'
        component.cnic = '12345-1234567-1'
        component.property_type = 'House'
        component.price = '300000'
        component.is_published = True
        
        # Save
        result = component.save()
        
        # Should redirect
        assert result is not None
        
        # Property should be created
        prop = Property.objects.get(name='New Property')
        assert prop.description == 'A beautiful new property'
        assert prop.price == Decimal('300000')
        assert prop.user == authenticated_request.user
    
    def test_edit_form_updates_existing_property(self, authenticated_request, property_factory, monkeypatch):
        """Test that edit form updates existing property correctly."""
        user = authenticated_request.user
        prop = property_factory(
            user=user,
            name='Old Name',
            price=Decimal('100000')
        )
        
        # Mock request.FILES methods
        monkeypatch.setattr(authenticated_request.FILES, 'getlist', lambda x: [])
        monkeypatch.setattr(authenticated_request.FILES, 'get', lambda x: None)
        
        component = PropertyFormView(
            component_id='test',
            component_name='property-form',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        # Update data
        component.name = 'New Name'
        component.price = '200000'
        
        # Save
        result = component.save()
        
        # Should redirect
        assert result is not None
        
        # Property should be updated
        prop.refresh_from_db()
        assert prop.name == 'New Name'
        assert prop.price == Decimal('200000')
    
    def test_non_owner_cannot_edit_property(self, authenticated_request, property_factory):
        """Test that non-owner cannot edit property."""
        other_user = User.objects.create_user(username='other', password='pass')
        prop = property_factory(user=other_user)
        
        component = PropertyFormView(
            component_id='test',
            component_name='property-form',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        # Should have error
        assert 'non_field' in component.errors
        assert 'permission' in component.errors['non_field'].lower()
    
    def test_document_removal_checkbox_works(self, authenticated_request, property_factory, monkeypatch):
        """Test that document removal checkbox works."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        user = authenticated_request.user
        
        # Create property with document
        prop = property_factory(user=user)
        prop.documents = SimpleUploadedFile('test.pdf', b'test content', content_type='application/pdf')
        prop.save()
        
        # Mock request.FILES methods
        monkeypatch.setattr(authenticated_request.FILES, 'getlist', lambda x: [])
        monkeypatch.setattr(authenticated_request.FILES, 'get', lambda x: None)
        
        component = PropertyFormView(
            component_id='test',
            component_name='property-form',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        # Mark document for removal
        component.remove_document = True
        
        # Save
        component.save()
        
        # Document should be removed
        prop.refresh_from_db()
        assert not prop.documents
    
    def test_image_toggle_delete(self, authenticated_request, property_factory):
        """Test that image toggle delete works."""
        user = authenticated_request.user
        prop = property_factory(user=user)
        
        # Create an image
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io
        
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        
        prop_image = PropertyImage.objects.create(
            property=prop,
            image=SimpleUploadedFile('test.jpg', img_io.read(), content_type='image/jpeg')
        )
        
        component = PropertyFormView(
            component_id='test',
            component_name='property-form',
            request=authenticated_request
        )
        component.property_id = prop.id
        component.mount()
        
        # Toggle image for deletion
        component.toggle_image_delete(prop_image.id)
        assert prop_image.id in component.images_to_delete
        
        # Toggle again to remove from deletion list
        component.toggle_image_delete(prop_image.id)
        assert prop_image.id not in component.images_to_delete
    
    def test_redirect_to_detail_page_after_save(self, authenticated_request, monkeypatch):
        """Test that form redirects to detail page after save."""
        # Mock request.FILES methods
        monkeypatch.setattr(authenticated_request.FILES, 'getlist', lambda x: [])
        monkeypatch.setattr(authenticated_request.FILES, 'get', lambda x: None)
        
        component = PropertyFormView(
            component_id='test',
            component_name='property-form',
            request=authenticated_request
        )
        component.mount()
        
        # Fill in valid data
        component.name = 'Test Property'
        component.description = 'Test description'
        component.full_address = 'Test address'
        component.phone_number = '+92-3001234567'
        component.cnic = '12345-1234567-1'
        component.property_type = 'House'
        component.price = '100000'
        
        # Save
        result = component.save()
        
        # Should return a redirect
        assert result is not None
        assert hasattr(result, 'url')
        # URL should contain the property ID
        assert result.url.startswith('/')
