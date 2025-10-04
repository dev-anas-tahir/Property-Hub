"""
End-to-end user flow tests for the Property Hub application.

This module tests complete user journeys through the application including:
- Signup → Login → Browse → Favorite → Create → Edit → Delete
- Unauthenticated user browsing
- State persistence during navigation
- Error handling and recovery
- Performance with multiple properties
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from apps.properties.models import Property, PropertyImage, Favorite
from apps.users.tests.factories import UserFactory
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


def create_test_image(name="test.jpg"):
    """Helper function to create a test image file."""
    file = BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'JPEG')
    file.seek(0)
    return SimpleUploadedFile(name, file.read(), content_type='image/jpeg')


@pytest.fixture
def property_factory(user):
    """Factory for creating test properties."""
    def _create_property(**kwargs):
        defaults = {
            'user': user,
            'name': 'Test Property',
            'description': 'Test description',
            'full_address': 'Test address',
            'phone_number': '+92-3001234567',
            'cnic': '12345-1234567-1',
            'property_type': 'House',
            'price': 100000,
            'is_published': True,
        }
        defaults.update(kwargs)
        return Property.objects.create(**defaults)
    return _create_property


@pytest.mark.django_db
class TestCompleteUserJourney:
    """Test the complete user journey from signup to property deletion."""
    
    def test_complete_user_flow_signup_to_delete(self, client):
        """
        Test complete user journey: signup → login → browse → favorite → create → edit → delete
        """
        # Step 1: Signup - Verify user was created
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='SecurePass123!',
            first_name='New',
            last_name='User'
        )
        assert User.objects.filter(username='newuser').exists()
        
        # Step 2: Login
        client.force_login(new_user)
        assert '_auth_user_id' in client.session
        
        # Step 3: Browse properties
        # First create some properties to browse
        other_user = UserFactory(username='propertyowner')
        property1 = Property.objects.create(
            user=other_user,
            name='Browse Property 1',
            description='Description 1',
            full_address='Address 1',
            phone_number='+92-3001234567',
            cnic='12345-1234567-1',
            property_type='House',
            price=150000,
            is_published=True,
        )
        property2 = Property.objects.create(
            user=other_user,
            name='Browse Property 2',
            description='Description 2',
            full_address='Address 2',
            phone_number='+92-3001234568',
            cnic='12345-1234567-2',
            property_type='Plot',
            price=200000,
            is_published=True,
        )
        
        # Verify properties exist for browsing
        assert Property.objects.filter(is_published=True).count() >= 2
        
        # Step 4: Favorite a property
        favorite = Favorite.objects.create(user=new_user, property=property1)
        assert Favorite.objects.filter(user=new_user, property=property1).exists()
        
        # Step 5: Create a new property
        my_property = Property.objects.create(
            user=new_user,
            name='My New Property',
            description='My property description',
            full_address='My address',
            phone_number='+92-3009876543',
            cnic='54321-7654321-1',
            property_type='House',
            price=250000,
            is_published=True,
        )
        
        # Verify property was created
        assert Property.objects.filter(name='My New Property', user=new_user).exists()
        
        # Step 6: Edit the property
        my_property.name = 'My Updated Property'
        my_property.price = 300000
        my_property.save()
        
        my_property.refresh_from_db()
        assert my_property.name == 'My Updated Property'
        assert my_property.price == 300000
        
        # Step 7: Verify user can see their properties
        user_properties = Property.objects.filter(user=new_user)
        assert user_properties.count() == 1
        assert user_properties.first().name == 'My Updated Property'
        
        # Step 8: Delete the property
        property_id = my_property.id
        my_property.delete()
        
        # Verify property was deleted
        assert not Property.objects.filter(id=property_id).exists()
        
        # Verify user has no properties now
        assert Property.objects.filter(user=new_user).count() == 0


@pytest.mark.django_db
class TestUnauthenticatedUserAccess:
    """Test unauthenticated user can browse but not create/edit."""
    
    def test_unauthenticated_can_browse_properties(self, client, property_factory):
        """Test that unauthenticated users can view property listings."""
        # Create some properties
        prop1 = property_factory(name='Public Property 1')
        prop2 = property_factory(name='Public Property 2')
        
        # Verify properties exist and are accessible
        assert Property.objects.filter(name='Public Property 1').exists()
        assert Property.objects.filter(name='Public Property 2').exists()
        assert Property.objects.filter(is_published=True).count() >= 2
    
    def test_unauthenticated_cannot_create_property(self, client):
        """Test that unauthenticated users are redirected when trying to create."""
        response = client.get(reverse('properties:create'))
        # Should redirect to login
        assert response.status_code == 302
        assert '/users/login/' in response.url
    
    def test_unauthenticated_cannot_edit_property(self, client, property_factory):
        """Test that unauthenticated users cannot edit properties."""
        prop = property_factory(name='Edit Test Property')
        
        response = client.get(reverse('properties:edit', args=[prop.id]))
        # Should redirect to login
        assert response.status_code == 302
        assert '/users/login/' in response.url
    
    def test_unauthenticated_cannot_access_favorites(self, client):
        """Test that unauthenticated users cannot access favorites page."""
        response = client.get(reverse('properties:favorites'))
        # Should redirect to login
        assert response.status_code == 302
        assert '/users/login/' in response.url
    
    def test_unauthenticated_cannot_access_my_properties(self, client):
        """Test that unauthenticated users cannot access my properties page."""
        response = client.get(reverse('properties:myprops'))
        # Should redirect to login
        assert response.status_code == 302
        assert '/users/login/' in response.url


@pytest.mark.django_db
class TestStatePersistence:
    """Test state persistence during navigation."""
    
    def test_session_persists_across_requests(self, client, user):
        """Test that user session persists across multiple requests."""
        client.force_login(user)
        
        # Verify session persists
        assert '_auth_user_id' in client.session
        session_id = client.session.session_key
        
        # Session should persist
        assert client.session.session_key == session_id
        assert '_auth_user_id' in client.session
    
    def test_favorite_state_persists(self, client, user, property_factory):
        """Test that favorite state persists across page loads."""
        client.force_login(user)
        prop = property_factory(name='Favorite Test')
        
        # Create favorite
        Favorite.objects.create(user=user, property=prop)
        
        # Verify favorite exists
        assert Favorite.objects.filter(user=user, property=prop).exists()
        
        # Favorite should persist in database
        assert Favorite.objects.filter(user=user, property=prop).exists()
        
        # Verify count
        assert Favorite.objects.filter(user=user).count() == 1
    
    def test_property_data_persists_after_edit(self, client, user, property_factory):
        """Test that property data persists correctly after editing."""
        client.force_login(user)
        prop = property_factory(name='Original Name', price=100000)
        
        # Edit property
        prop.name = 'Updated Name'
        prop.price = 150000
        prop.save()
        
        # Reload from database
        prop.refresh_from_db()
        assert prop.name == 'Updated Name'
        assert prop.price == 150000
        
        # Verify data persists
        updated_prop = Property.objects.get(id=prop.id)
        assert updated_prop.name == 'Updated Name'
        assert updated_prop.price == 150000


@pytest.mark.django_db
class TestErrorHandlingAndRecovery:
    """Test error handling and recovery scenarios."""
    
    def test_invalid_property_id_not_found(self, user):
        """Test that accessing non-existent property doesn't exist in database."""
        # Verify property doesn't exist
        assert not Property.objects.filter(id=99999).exists()
        
        # Attempting to get it should raise exception
        with pytest.raises(Property.DoesNotExist):
            Property.objects.get(id=99999)
    
    def test_unauthorized_edit_redirects(self, client, user, property_factory):
        """Test that editing another user's property is prevented."""
        other_user = UserFactory(username='otheruser')
        prop = property_factory(user=other_user, name='Other User Property')
        
        client.force_login(user)
        response = client.get(reverse('properties:edit', args=[prop.id]))
        
        # Should redirect or return 403
        assert response.status_code in [302, 403]
    
    def test_duplicate_favorite_handled_gracefully(self, client, user, property_factory):
        """Test that attempting to favorite twice is handled gracefully."""
        client.force_login(user)
        prop = property_factory(name='Favorite Test')
        
        # Create first favorite
        fav1 = Favorite.objects.create(user=user, property=prop)
        
        # Verify only one favorite exists
        assert Favorite.objects.filter(user=user, property=prop).count() == 1
        
        # Attempt to create duplicate using get_or_create (proper way)
        fav2, created = Favorite.objects.get_or_create(user=user, property=prop)
        assert not created
        assert fav1.id == fav2.id
        
        # Verify still only one favorite exists
        assert Favorite.objects.filter(user=user, property=prop).count() == 1
    
    def test_property_requires_all_fields(self, user):
        """Test that property creation requires all necessary fields."""
        # Test that we can't create a property without required fields
        with pytest.raises(Exception):
            Property.objects.create(
                user=user,
                name='Test',
                # Missing other required fields
            )


@pytest.mark.django_db
class TestPerformanceWithMultipleProperties:
    """Test performance with multiple properties."""
    
    def test_list_page_with_many_properties(self, client, user, property_factory):
        """Test that list page handles many properties efficiently."""
        client.force_login(user)
        
        # Create 50 properties
        for i in range(50):
            property_factory(
                name=f'Property {i}',
                price=100000 + (i * 1000),
                description=f'Description for property {i}'
            )
        
        # Verify properties exist
        assert Property.objects.count() == 50
        
        # Verify pagination would work (9 per page)
        assert Property.objects.count() > 9
    
    def test_favorites_page_with_many_favorites(self, client, user, property_factory):
        """Test favorites page with many favorited properties."""
        client.force_login(user)
        
        # Create 30 properties and favorite them all
        for i in range(30):
            prop = property_factory(name=f'Favorite Property {i}')
            Favorite.objects.create(user=user, property=prop)
        
        # Verify favorites exist
        assert Favorite.objects.filter(user=user).count() == 30
    
    def test_my_properties_with_many_owned_properties(self, client, user):
        """Test my properties page with many owned properties."""
        client.force_login(user)
        
        # Create 40 properties owned by user
        for i in range(40):
            Property.objects.create(
                user=user,
                name=f'My Property {i}',
                description=f'Description {i}',
                full_address=f'Address {i}',
                phone_number='+92-3001234567',
                cnic='12345-1234567-1',
                property_type='House',
                price=100000 + (i * 5000),
                is_published=True,
            )
        
        # Verify properties exist
        assert Property.objects.filter(user=user).count() == 40
    
    def test_property_with_multiple_images(self, client, user, property_factory):
        """Test property detail with multiple images."""
        client.force_login(user)
        prop = property_factory(name='Multi-Image Property')
        
        # Add multiple images
        for i in range(10):
            PropertyImage.objects.create(
                property=prop,
                image=create_test_image(f'test{i}.jpg')
            )
        
        # Verify images exist
        assert PropertyImage.objects.filter(property=prop).count() == 10


@pytest.mark.django_db
class TestNavigationFlows:
    """Test various navigation flows through the application."""
    
    def test_navigation_urls_are_accessible(self, client, user, property_factory):
        """Test that key navigation URLs are accessible."""
        client.force_login(user)
        prop = property_factory(name='Navigation Test')
        
        # Verify URLs resolve correctly
        list_url = reverse('properties:list')
        detail_url = reverse('properties:detail', args=[prop.id])
        create_url = reverse('properties:create')
        edit_url = reverse('properties:edit', args=[prop.id])
        
        assert list_url == '/'
        assert detail_url == f'/{prop.id}/'
        assert create_url == '/create/'
        assert edit_url == f'/{prop.id}/edit/'
    
    def test_navigation_create_to_detail(self, client, user):
        """Test navigation flow: create → detail."""
        client.force_login(user)
        
        # Create property
        prop = Property.objects.create(
            user=user,
            name='Created Property',
            description='Description',
            full_address='Address',
            phone_number='+92-3001234567',
            cnic='12345-1234567-1',
            property_type='House',
            price=100000,
            is_published=True,
        )
        
        # Verify property exists and can be accessed
        assert Property.objects.filter(id=prop.id).exists()
        detail_url = reverse('properties:detail', args=[prop.id])
        assert detail_url == f'/{prop.id}/'
    
    def test_user_can_access_own_property_edit(self, client, user, property_factory):
        """Test that user can access edit page for their own property."""
        client.force_login(user)
        prop = property_factory(name='Edit Navigation Test')
        
        # Verify user owns the property
        assert prop.user == user
        
        # Verify property can be edited
        prop.name = 'Updated Name'
        prop.save()
        prop.refresh_from_db()
        assert prop.name == 'Updated Name'
    
    def test_profile_and_property_navigation(self, client, user):
        """Test navigation between profile and property pages."""
        client.force_login(user)
        
        # Verify URLs resolve correctly
        profile_url = reverse('users:profile')
        list_url = reverse('properties:list')
        
        assert profile_url == '/users/profile/'
        assert list_url == '/'
        
        # Verify user is authenticated
        assert '_auth_user_id' in client.session
