from django.apps import AppConfig


class CasesConfig(AppConfig):
    name = 'cases'

    def ready(self):
        """
        App configuration here.

        """
        # Configuration for the signals module.
        import cases.signals
        # Register tag model Service as "Action Object" for django-activity-stream
        from actstream import registry
        registry.register(self.get_model('Case'))
