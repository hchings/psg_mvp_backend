"""
Database models for clinic

"""
import os
import coloredlogs, logging

from phonenumber_field.modelfields import PhoneNumberField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from imagekit.models import ImageSpecField
from elasticsearch_dsl.exceptions import ValidationException

# from taggit.managers import TaggableManager
# from django import forms
# from django.db import models
from djongo import models
from hanziconv import HanziConv

from django import forms
from django.conf import settings
# from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model
from django.core.management import call_command

# from backend.shared.models import SimpleString, SimpleStringForm
from backend.shared.fields import MongoDecimalField
from ..doc_type import ClinicProfileDoc


# from django.utils.translation import ugettext_lazy as _

# from tags.models import ServiceTaggedItem

# Create a logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

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
    opening_info = models.CharField(max_length=200, default='', blank=True)

    # store a json object
    # {'11:00-20:00': [1,2,3,4,5,6]
    #  'close': [7]
    # }
    opening_concise = models.CharField(max_length=200, default='', blank=True)

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

    # geo info
    longitude = MongoDecimalField(max_digits=9, decimal_places=6, blank=True)
    latitude = MongoDecimalField(max_digits=9, decimal_places=6, blank=True)

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

    # average of the ratings of all branches
    @property
    def rating(self):
        """
        Simply average the ratings from all its branches.

        :return (float): the averaged ratings
        """
        # TODO: add prevention on user type?
        branch_ratings = [branch.rating for branch in self.branches if branch.rating]
        # arithmetic average rounded to 1 decimal point
        return 0.0 if not branch_ratings else round(sum(branch_ratings)/len(branch_ratings), 1)

    # services_raw = models.ArrayModelField(
    #     model_container=SimpleString,
    #     model_form_class=SimpleStringForm,
    #     default=[]
    # )

    services_raw_input = models.TextField(blank=True, help_text="隆鼻, 雙眼皮, 抽脂, ... \
                                                                 Type '-' to clear the service_raw field")
    services_raw = models.ListField(blank=True,
                                    default=[],
                                    help_text="the original service tags on official sites w/out any normalization")

    # tags
    # services = TaggableManager(through=ServiceTaggedItem, blank=True)

    def __str__(self):
        return 'clinic_profile_' + self.display_name

    def indexing(self):
        """
        An indexing instance method that adds the object instance
        to the Elasticsearch index via the DocType we just created.

        :return:
        """
        # tmp turn off elastic search
        return

        id = str(getattr(self, '_id', ''))

        # Simplified CN's analyzer is much better.
        # so all the cn fields will be stored in simplified chinese in ES.
        doc = ClinicProfileDoc(
            meta={'id': id},  # each document has metadata associated with it
            display_name=HanziConv.toSimplified(self.display_name),
            obsolete_name=HanziConv.toSimplified(self.obsolete_name),
            english_name=self.english_name,
            id=id  # we need this field to fetch the matched doc from mongo
        )

        try:
            doc.save()
        except ValidationException as e:
            # trigger index_clinic_profiles command to create index and load all
            # current records to ES.
            logger.error("Error while saving ClinicProfile and update ES index: %s" % str(e))
            call_command('index_clinic_profiles')

        return doc.to_dict(include_meta=True)
