"""
Database model for clinic profiles

"""
# from phonenumber_field.modelfields import PhoneNumberField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
# from taggit.managers import TaggableManager
from django import forms
# from django.db import models
from djongo import models
# from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model
# from django.utils.translation import ugettext_lazy as _

# from tags.models import ServiceTaggedItem


# TODO: clean this up
# -------------------------------
#            Utilities
# -------------------------------

def get_logo_full_dir_name(instance, filename):
    extension = filename.split(".")[-1]
    new_filename = 'logo_full.' + extension
    return '/'.join(['clinics', 'clinic_' + str(instance.user.uuid), new_filename])


def get_logo_dir_name(instance, filename):
    """
    Normalize the dir and file name of the logo img.
    :return(str): the relative dir path
    """
    user_model = get_user_model()
    clinic = user_model.objects.get(_id=instance.user_id)
    extension = filename.split(".")[-1]
    new_filename = 'logo.' + extension
    return '/'.join(['clinics', 'clinic_' + str(clinic.uuid), new_filename])


def get_doctor_dir_name(instance, filename):
    extension = filename.split(".")[-1]
    new_filename = 'profile_photo.' + extension
    return '/'.join(['doctors', 'doctor_' + str(instance.user.uuid), new_filename])


class ClinicProfile(models.Model):
    """
    Clinic Profile model.
    One-on-one relationship to User model by storing ObjectId in user_id.

    """

    _id = models.ObjectIdField()
    # user = models.OneToOneField(get_user_model(),
    #                             related_name='clinic_profile',
    #                             on_delete=models.CASCADE) #tmp
    # tmp = models.EmbeddedModelField(model_container=Blog,
    #                                 model_form_class=UserForm
    #                                 )
    # user = models.EmbeddedModelField(model_container=get_user_model())
    # user = models.EmbeddedModelField(model_container=get_user_model())
    user_id = models.CharField(max_length=30,
                               blank=False)

    display_name = models.CharField(max_length=30,
                                    blank=False)

    english_name = models.CharField(max_length=50,
                                    default='',
                                    blank=True)

    # TODO: check params and path
    # logo_full = models.ImageField(upload_to=get_logo_full_dir_name,
    #                               blank=True,
    #                               null=True,
    #                               help_text="logo with clinic name")
    # logo = models.ImageField(upload_to=get_logo_dir_name,
    #                          blank=True,
    #                          null=True,
    #                          help_text="pure logo in square")

    # Image is resized to 120X120 pixels with django-imagekit
    logo = ProcessedImageField(upload_to=get_logo_dir_name,
                               processors=[ResizeToFill(120, 120)],
                               format='JPEG',
                               options={'quality': 90},
                               blank=True,
                               null=True,
                               help_text="pure logo in square")
    #
    # # main service if the website does specify
    # slogan = models.CharField(max_length=30,
    #                           default='',
    #                           blank=True)
    #
    # color_code = models.CharField(blank=True, default='', max_length=20)
    #
    website_url = models.URLField(blank=True)
    fb_url = models.URLField(blank=True)
    weibo_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    line_id = models.CharField(max_length=50, default='', blank=True)
    wechat_id = models.CharField(max_length=50, default='', blank=True)
    customer_email = models.EmailField(max_length=254, blank=True, verbose_name='email address')
    #
    # # tsgs
    # services = TaggableManager(through=ServiceTaggedItem, blank=True)

    def __str__(self):
        return 'clinic_profile_' + self.display_name
#
#
# class ClinicBranch(models.Model):
#     """
#     Represent the info of a clinic branch including
#     location, etc.
#     Many-to-one relationship to ClinicProfile.
#
#     """
#     # one-to-many field
#     clinic_group = models.ForeignKey(ClinicProfile,
#                                      related_name="branches",
#                                      on_delete=models.CASCADE,  # not sure
#                                      help_text="the clinic group")
#
#     # --- basic info ---
#     place_id = models.CharField(max_length=50,
#                                 blank=True,
#                                 help_text="unique google place_id")
#     is_head_quarter = models.BooleanField(default=False, blank=True)
#
#     # TODO: this seems needed to be filled manually..
#     branch_name = models.CharField(max_length=50)
#
#     # --- opening info ---
#     # store a json object
#     # {'11:00-20:00': [1,2,3,4,5,6]
#     #  'close': [7]
#     # }
#     opening_info = models.CharField(max_length=200, default='', blank=True)
#
#     # --- atmosphere info ---
#     rating = models.FloatField(help_text="ratings from google map API",
#                                null=True,
#                                blank=True)
#
#     # --- address info ---
#     # TODO: should refactor into an address model.
#     # TODO: manual address won't have region and local
#     address = models.CharField(max_length=100, default='', blank=True)
#     address_help_text = models.CharField(max_length=100, default='', blank=True)
#     region = models.CharField(max_length=20, default='', blank=True)
#     locality = models.CharField(max_length=20, default='', blank=True)
#
#     # most starts with nationality code (+XXX)
#     # otherwise it will be considered invalid.
#     phone = PhoneNumberField(blank=True)
#
#     def __str__(self):
#         return self.clinic_group.user.username + '_' + self.branch_name
