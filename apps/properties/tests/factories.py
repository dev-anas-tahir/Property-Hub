import factory

from apps.properties.models import Favorite, Property
from apps.shared.tests.factories import UserFactory


class PropertyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Property

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Property {n}")
    full_address = factory.Faker("address")
    phone_number = "+92-3001234567"
    cnic = "12345-1234567-1"
    property_type = "House"
    price = factory.Faker("pydecimal", left_digits=6, right_digits=2, positive=True)
    is_published = True


class FavoriteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Favorite

    user = factory.SubFactory(UserFactory)
    property = factory.SubFactory(PropertyFactory)
