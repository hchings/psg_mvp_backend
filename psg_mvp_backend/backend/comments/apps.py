from django.apps import AppConfig


class CommentsConfig(AppConfig):
    name = 'comments'

    def ready(self):
        """
        App configuration here.

        """
        # Configuration for the signals module.
        import comments.signals
        # Register tag model Service as "Action Object" for django-activity-stream
        from actstream import registry
        registry.register(self.get_model('Comment'))
