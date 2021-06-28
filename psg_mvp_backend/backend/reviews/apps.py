from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    name = 'reviews'

    def ready(self):
        """
        App configuration here

        """
        # Configuration for the signals module.
        import reviews.signals
