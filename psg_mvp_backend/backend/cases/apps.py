from django.apps import AppConfig


class CasesConfig(AppConfig):
    name = 'cases'

    def ready(self):
        """
        App configuration here.

        """
        # Configuration for the signals module.
        import cases.signals

        # Configuration for the cache signal
        import cases.cache_signals
        import cases.cache_receivers

        # Register tag model Service as "Action Object" for django-activity-stream
        from actstream import registry
        registry.register(self.get_model('Case'))
