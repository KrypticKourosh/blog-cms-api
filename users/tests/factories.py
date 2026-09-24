import factory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.declarations.Sequence(lambda n: f'user{n}')
    email = factory.declarations.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.declarations.PostGenerationMethodCall('set_password', 'string1234')