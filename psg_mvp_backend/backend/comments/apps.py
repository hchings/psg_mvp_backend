from django.apps import AppConfig


class CommentsConfig(AppConfig):
    name = 'comments'

    def ready(self):
        """
        App configuration here.

        """
        # Configuration for the signals module.
        import comments.signals
