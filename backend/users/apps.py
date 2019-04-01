"""
Users app configurations.

"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        """
        App configuration here.

        """
        # Configuration for the signals module.
        import users.signals
        # Register model User as "Actor" for django-activity-stream
        # from actstream import registry
        # registry.register(self.get_model('User'))
