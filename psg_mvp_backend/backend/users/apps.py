"""
Users app configurations.

"""

from elasticsearch_dsl import connections
from django.apps import AppConfig
from django.conf import settings


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

        # elastic search connection
        try:
            res = connections.create_connection('default',
                                                hosts=[{'host': settings.ES_HOST, 'port': settings.ES_PORT}])
        except Exception as e:
            print(e)

        # Register tag model Service as "Action Object" for django-activity-stream
        from actstream import registry
        registry.register(self.get_model('User'))
        registry.register(self.get_model('ClinicProfile'))

