from django.apps import AppConfig


class TagsConfig(AppConfig):
    name = 'tags'



# from django.apps import AppConfig
#
#
# class TagsConfig(AppConfig):
#     name = 'tags'
#
#     def ready(self):
#         """
#         App configuration here.
#
#         """
#         # Register tag model Service as "Actor" for django-activity-stream
#         from actstream import registry
#         registry.register(self.get_model('Service'))
