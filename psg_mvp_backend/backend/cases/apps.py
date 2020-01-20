from django.apps import AppConfig


class CasesConfig(AppConfig):
    name = 'cases'

    def ready(self):
        """
        App configuration here.

        """
        # Configuration for the signals module.
        import cases.signals
