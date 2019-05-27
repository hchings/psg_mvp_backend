# from taggit.models import GenericTaggedItemBase, TagBase
#
# from django.db import models
#
#
# class RawService(TagBase):
#     pass
#
#
# class RawServiceTaggedItem(GenericTaggedItemBase):
#     tag = models.ForeignKey(RawService,
#                             related_name='raw_service_tagged',
#                             on_delete=models.CASCADE)

#
# # service tags
# class Service(TagBase):
#     """
#     Tagging model representing service.
#     (TagBase is the base db model in django-taggit)
#
#     """
#     methods = TaggableManager(through=MethodTaggedItem, blank=True)
#
#
# class ServiceTaggedItem(GenericTaggedItemBase):
#     """
#     Intermediate models.
#
#     """
#     # TODO: not sure about related_name
#     tag = models.ForeignKey(Service,
#                             related_name='service_tagged',
#                             on_delete=models.CASCADE)
#
#     methods = TaggableManager(through=MethodTaggedItem, blank=True)

#
# class RawService(models.Model):
#
#     tags = TaggableManager()
# #