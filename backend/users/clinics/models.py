"""
Database models for clinic

"""
import os

from phonenumber_field.modelfields import PhoneNumberField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from imagekit.models import ImageSpecField
# from taggit.managers import TaggableManager
# from django import forms
# from django.db import models
from djongo import models
from django import forms
from django.conf import settings
# from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model


# from django.utils.translation import ugettext_lazy as _

# from tags.models import ServiceTaggedItem


# -------------------------------
#            Utilities
# -------------------------------

def get_logo_full_dir_name(instance, filename):
    extension = filename.split(".")[-1]
    new_filename = 'logo_full.' + extension
    return os.path.join(settings.MEDIA_ROOT, '/'.join(['clinics', 'clinic_' + str(instance.user.uuid), new_filename]))


def get_logo_dir_name(instance, filename):
    """
    Normalize the dir and file name of the logo img.
    :return(str): the relative dir path
    """
    user_model = get_user_model()
    clinic = user_model.objects.get(_id=instance.user_id)
    extension = filename.split(".")[-1]
    new_filename = 'logo.' + extension
    # obj.log.url, Media root is by default loaded
    return os.path.join('clinics', 'clinic_' + str(clinic.uuid), new_filename)


class ClinicBranch(models.Model):
    """
    Abstract model representing the info of a clinic branch.
    Many-to-one relationship to ClinicProfile.

    """

    class Meta:
        abstract = True

    # # one-to-many field. no need this when using mongo
    # clinic_group = models.ForeignKey(ClinicProfile,
    #                                  related_name="branches",
    #                                  on_delete=models.CASCADE,  # not sure
    #                                  help_text="the clinic group")

    # --- basic info ---
    place_id = models.CharField(max_length=50,
                                blank=True,
                                help_text="unique google place_id")
    is_exact_place_id = models.BooleanField(default=True,
                                            help_text="whether the clinic has Google Business ID")
    is_head_quarter = models.BooleanField(default=False, blank=True)
    branch_name = models.CharField(max_length=50)

    # --- opening info ---
    # store a json object
    # {'11:00-20:00': [1,2,3,4,5,6]
    #  'close': [7]
    # }
    opening_info = models.CharField(max_length=200, default='', blank=True)

    # --- atmosphere info ---
    rating = models.FloatField(help_text="ratings from google map API",
                               blank=True)

    # --- address info ---
    address = models.CharField(max_length=100, default='', blank=True)
    address_help_text = models.CharField(max_length=100, default='', blank=True)
    region = models.CharField(max_length=20, default='', blank=True)
    locality = models.CharField(max_length=20, default='', blank=True)

    # most starts with nationality code (+XXX) otherwise considered invalid.
    phone = PhoneNumberField(blank=True)

    def __str__(self):
        return self.branch_name


class ClinicBranchForm(forms.ModelForm):
    """
    Customize form for ArrayModelField from djongo bcz
    the self-generated Form has all fields set to required.
    """

    class Meta:
        model = ClinicBranch
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ClinicBranchForm, self).__init__(*args, **kwargs)
        # all fields are not required except for branch_name
        for key, _ in self.fields.items():
            if key not in ['branch_name']:
                self.fields[key].required = False


class ClinicProfile(models.Model):
    """
    Clinic Profile model.
    Relationship with other models:
    - User model: a fake one-on-one relationship by storing ObjectId and
                  uuid of the corresponding User.
    - ClinicBranch model: ArrayModelFields (embedded)

    Auto-created when a clinic user is created.

    """

    _id = models.ObjectIdField()

    # ---fields copy from the User colleciton ---
    user_id = models.CharField(max_length=30,
                               blank=False,
                               editable=False,
                               help_text="the _id field of the User collection. Do not fill in this manually.")
    uuid = models.CharField(max_length=30,
                            unique=True,
                            editable=False,
                            help_text="the uuid field in the corresponding user. Do not fill in this manually.")

    display_name = models.CharField(max_length=30, blank=False)
    obsolete_name = models.CharField(max_length=30,
                                     blank=True,
                                     help_text="the original names for clinics who changed their names")
    english_name = models.CharField(max_length=50,
                                    default='',
                                    blank=True)

    obsolete_english_name = models.CharField(max_length=50,
                                             blank=True)

    # TODO: check params and path
    # logo_full = models.ImageField(upload_to=get_logo_full_dir_name,
    #                               blank=True,
    #                               null=True,
    #                               help_text="logo with clinic name")

    # Image is resized to 120X120 pixels with django-imagekit
    logo = ProcessedImageField(upload_to=get_logo_dir_name,
                               processors=[ResizeToFill(400, 400)],
                               format='JPEG',
                               options={'quality': 100},
                               blank=True,
                               null=True,
                               help_text="pure logo in square")

    # logo = models.ImageField(upload_to=get_logo_dir_name)
    logo_thumbnail = ImageSpecField(source='logo',
                                    processors=[ResizeToFill(130, 130)],
                                    format='JPEG',
                                    options={'quality': 100})

    # main service if the website does specify
    slogan = models.CharField(max_length=30,
                              default='',
                              blank=True)

    color_code = models.CharField(blank=True, default='', max_length=20)
    phone = PhoneNumberField(blank=True, help_text="general customer service phone")

    # --- social media ---
    website_url = models.URLField(blank=True)
    fb_url = models.URLField(blank=True)
    weibo_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    wechat_url = models.URLField(blank=True, help_text="wechat QR code url")
    line_url = models.URLField(blank=True, help_text="line QR code url")
    youtube_url = models.URLField(blank=True, help_text="youtube channel")
    pixnet_url = models.URLField(blank=True)

    line_id = models.CharField(max_length=50, default='', blank=True)
    wechat_id = models.CharField(max_length=50, default='', blank=True)
    customer_email = models.EmailField(max_length=254, blank=True, verbose_name='email address')

    # --- for internal user only ---
    first_check = models.BooleanField(default=False, blank=True, help_text="first manual data checking")
    all_doctors_loaded = models.BooleanField(default=False, blank=True, help_text="has doctors in the db")
    is_sm = models.BooleanField(default=False, blank=True, help_text="is small. for marking tiny clinics")
    is_oob = models.BooleanField(default=False, blank=True, help_text="might be out-of-business")

    # branches = models.EmbeddedModelField(model_container=ClinicBranch)
    branches = models.ArrayModelField(
        model_container=ClinicBranch,
        model_form_class=ClinicBranchForm,
        default=[]
    )

    # tags
    # services = TaggableManager(through=ServiceTaggedItem, blank=True)

    def __str__(self):
        return 'clinic_profile_' + self.display_name
