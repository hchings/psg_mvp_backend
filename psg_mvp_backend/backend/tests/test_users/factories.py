import factory

from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = 'testuser'
    password = factory.PostGenerationMethodCall('set_password', 'testpassword')
    email = 'testuser@test.com'
    is_superuser = False
    is_staff = False
    is_active = True


class AdminUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = 'testadminuser'
    password = factory.PostGenerationMethodCall('set_password', 'testpassword')
    email = 'testadminuser@test.com'
    is_superuser = True
    is_staff = True
    is_active = True
