"""Extra model tests for properties: published manager, primary image and favorites."""

import pytest
from apps.properties.models import Property, PropertyImage, Favorite


@pytest.mark.django_db
def test_published_manager(user):
    # two properties, one published
    Property.objects.create(user=user, name="P1", full_address="A", phone_number="+923001234567", cnic="12345-1234567-1", property_type="House", description="d", price=100)
    Property.objects.create(user=user, name="P2", full_address="B", phone_number="+923001234567", cnic="12345-1234567-1", property_type="Plot", description="d2", price=200, is_published=True)

    all_props = Property.objects.all()
    published = Property.published.all()

    assert all_props.count() >= 2
    assert published.count() == 1
    assert published.first().name == "P2"


@pytest.mark.django_db
def test_primary_image_selection(user):
    prop = Property.objects.create(user=user, name="WithImages", full_address="A", phone_number="+923001234567", cnic="12345-1234567-1", property_type="House", description="d", price=100)
    img1 = PropertyImage.objects.create(property=prop, image="img1.jpg", is_primary=False)
    img2 = PropertyImage.objects.create(property=prop, image="img2.jpg", is_primary=True)
    img3 = PropertyImage.objects.create(property=prop, image="img3.jpg", is_primary=False)

    primary = prop.primary_image()
    assert primary is not None
    assert primary.pk == img2.pk


@pytest.mark.django_db
def test_favorite_uniqueness(user):
    prop = Property.objects.create(user=user, name="FavProp", full_address="A", phone_number="+923001234567", cnic="12345-1234567-1", property_type="House", description="d", price=100)
    # use get_or_create to safely assert uniqueness semantics across DBs
    fav1, created1 = Favorite.objects.get_or_create(user=user, property=prop)
    fav2, created2 = Favorite.objects.get_or_create(user=user, property=prop)

    assert fav1.pk == fav2.pk
    assert created1 is True
    assert created2 is False
