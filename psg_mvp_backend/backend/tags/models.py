"""
Database models for tags.

"""

# from taggit.models import GenericTaggedItemBase, TagBase
#
# import os, json
# from backend.settings import FIXTURE_ROOT

from djongo import models


# note that this is relevant to the top app folder
# CATALOG_FILE = os.path.join(FIXTURE_ROOT, 'catalog.json')
# CATE_OPTIONS = ()
#
# # load Cate_options
# with open(CATALOG_FILE) as json_file:
#     catalog_dict = json.load(json_file)
#
# for item in catalog_dict.get('catalog_items', []):
#     category = item.get("category", "")
#     if category:
#         CATE_OPTIONS.append(category)


class Service(models.Model):
    CATE_OPTIONS = (
        ('', ''),
        ('face', '臉輪廓'),
        ('eyes', '眼部'),
        ('nose', '鼻型'),
        ('breast', '胸型'),
        ('lip', '唇部'),
        ('abs', '腰腹瘦身'),
        ('butt', '臀部'),
        ('arms', '手臂'),
        ('legs', '腿部'),
        ('skin', '皮膚美容'),
        ('ears', '耳部'),  # not in catalog.json
        ('private', '私密處'),  # not in catalog.json
        ('others', '其他'),  # not in catalog.json
    )

    _id = models.ObjectIdField()

    # id = models.AutoField(primary_key=True,
    #                       unique=True,
    #                       help_text="unique service id")

    category = models.CharField(max_length=15,
                                choices=CATE_OPTIONS,
                                default=0)

    name = models.CharField(max_length=30,
                            blank=False,
                            help_text="service name")

    is_invasive = models.BooleanField(default=False,
                                      help_text="set to true if it's invasive surgery")

    syns = models.ListField(blank=True,
                            default=[],
                            help_text="a collection of synonyms of this service")

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


# class Service(models.Model):
#     pass
