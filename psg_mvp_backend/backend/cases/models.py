"""
Database models for cases

"""
from datetime import date
import os

from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFill
from djongo import models

from django.conf import settings
from django import forms
from backend.shared.utils import make_id
from .doc_type import CaseDoc


YEAR_CHOICES = [(y, y) for y in range(2000, date.today().year + 1)]
MONTH_CHOICE = [(m, m) for m in range(1, 13)]


############################################################
#   For getting img file names and paths
#   TODO: could use decorator to simplify. But unimportant.
############################################################

def get_bg_img_dir_name(instance, filename):
    """
    Normalize the dir and file name of the before img.
    :return(str): the relative dir path
    """
    extension = filename.split(".")[-1]
    new_filename = 'before.' + extension
    # obj.log.url, Media root is by default loaded
    # adding MEDIA_ROOT is wrong! the below two will save the img to the same place,
    # but the upper one will be wrong when serialized.
    # return os.path.join(settings.MEDIA_ROOT, '/'.join(['cases', 'case_' + str(instance.uuid), new_filename]))
    return '/'.join(['cases', 'case_' + str(instance.uuid), new_filename]) # TODO: tmp try


def get_bg_img_cropped_dir_name(instance, filename):
    """
    Normalize the dir and file name of the cropped before img.
    :return(str): the relative dir path
    """
    extension = filename.split(".")[-1]
    new_filename = 'before_cropped.' + extension
    # obj.log.url, Media root is by default loaded
    return '/'.join(['cases', 'case_' + str(instance.uuid), new_filename])


def get_af_img_dir_name(instance, filename):
    """
    Normalize the dir and file name of the after img.
    :return(str): the relative dir path
    """
    extension = filename.split(".")[-1]
    new_filename = 'after.' + extension
    # obj.log.url, Media root is by default loaded
    return '/'.join(['cases', 'case_' + str(instance.uuid), new_filename])


def get_af_img_cropped_dir_name(instance, filename):
    """
    Normalize the dir and file name of the cropped after img.
    :return(str): the relative dir path
    """
    extension = filename.split(".")[-1]
    new_filename = 'after_cropped.' + extension
    # obj.log.url, Media root is by default loaded
    return '/'.join(['cases', 'case_' + str(instance.uuid), new_filename])


def get_case_dir_name(instance, filename):
    return '/'.join(['cases', 'case_' + str(instance.case_uuid), filename])


############################################################
#   Djongo's Abstract Model
############################################################

class SurgeryTag(models.Model):
    """
    Abstract model representing the info of a surgery tag.
    Many-to-one relationship to Case.
    """

    class Meta:
        abstract = True

    name = models.CharField(max_length=30, blank=True)
    mat = models.CharField(max_length=15,
                           blank=True,
                           help_text="surgery material")

    # must implement this
    def __str__(self):
        return '%s (%s)' % (self.name, self.mat) if self.mat else self.name


class SurgeryTagForm(forms.ModelForm):
    """
    Customize form for SurgeryTag from djongo bcz
    the self-generated Form has all fields set to required.
    """

    class Meta:
        model = SurgeryTag
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SurgeryTagForm, self).__init__(*args, **kwargs)
        # all fields are not required except for branch_name
        for key, _ in self.fields.items():
            self.fields[key].required = False


class UserInfo(models.Model):
    """
    Abstract model representing the info of a author.
    one-to-one relationship to Case.
    TODO: add relationship if pbm=True
    """

    class Meta:
        abstract = True

    name = models.CharField(max_length=30, blank=True)
    uuid = models.CharField(max_length=30,
                            blank=False,
                            help_text="the uuid field in the corresponding user. Do not fill in this manually.")

    def __str__(self):
        return self.name


class UserInfoForm(forms.ModelForm):
    """
    Customize form for UserInfo from djongo bcz
    the self-generated Form has all fields set to required.
    """

    class Meta:
        model = UserInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserInfoForm, self).__init__(*args, **kwargs)
        # all fields are not required except for branch_name
        for key, _ in self.fields.items():
            self.fields[key].required = False


class ClinicInfo(models.Model):
    """
    Abstract model representing the info of a clinic.
    one-to-one relationship to Case.
    """

    class Meta:
        abstract = True

    display_name = models.CharField(max_length=30, blank=False)
    branch_name = models.CharField(max_length=20, blank=False)

    # to get branch name
    place_id = models.CharField(max_length=50,
                                blank=True,
                                help_text="unique google place_id")
    # editable = False,
    uuid = models.CharField(max_length=30,
                            blank=False,
                            help_text="the uuid field in the corresponding clinic. Do not fill in this manually.")

    doctor_name = models.CharField(max_length=30, blank=True)

    # must add this otherwise can't print
    def __str__(self):
        return self.display_name


class SurgeryMeta(models.Model):
    """
    Abstract model representing the meta info of a Case.
    one-to-one relationship to Case.
    """

    # default = datetime.datetime.now().year,
    # default = datetime.datetime.now().month,

    class Meta:
        abstract = True

    year = models.IntegerField(choices=YEAR_CHOICES, null=True)
    month = models.IntegerField(choices=MONTH_CHOICE, null=True)
    dateString = models.CharField(max_length=60, blank=True, null=True)
    min_price = models.PositiveIntegerField(blank=True, null=True)
    max_price = models.PositiveIntegerField(blank=True, null=True)

    # + price breakdown?

    def __str__(self):
        return str(self.year)  # tmp


class SurgeryMetaForm(forms.ModelForm):
    """
    Customize form for SurgeryMeta from djongo bcz
    the self-generated Form has all fields set to required.
    """

    class Meta:
        model = SurgeryMeta
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SurgeryMetaForm, self).__init__(*args, **kwargs)
        # all fields are not required except for branch_name
        for key, _ in self.fields.items():
            # if key not in ['branch_name']:
            self.fields[key].required = False


class CaseImages(models.Model):
    """
    Concrete model for storing cases images other
    than before/after photos. TODO: WIP
    """
    # post = models.ForeignKey(Post, default=None)
    # image = models.ImageField(upload_to=get_image_filename,
    #                           verbose_name='Image')

    # Image is resized to 120X120 pixels with django-imagekit
    # when you don't want to save the ori image
    img = ProcessedImageField(upload_to=get_case_dir_name,
                              processors=[ResizeToFill(1000, 750)],
                              format='JPEG',
                              options={'quality': 100},
                              blank=True,
                              null=True)

    img_thumb = ImageSpecField(source='img',
                               processors=[ResizeToFill(520, 390)],
                               format='JPEG',
                               options={'quality': 100})

    caption = models.CharField(max_length=50,
                               default='',
                               blank=True)

    # editable = False,
    case_uuid = models.CharField(max_length=30,
                                 blank=False,
                                 unique=False,
                                 help_text="the uuid field in the corresponding case. Do not fill in this manually.")

    # 798 X 350 4:3
    # 1000 X 750


# TODO: add delete photo stuff/signal
class Case(models.Model):
    """
    The core model for a case.
    """
    STATES = (
        ('draft', 'draft'),
        ('reviewing', 'reviewing'),
        ('published', 'published'),
        ('hidden', 'hidden'),
    )

    GENDERS = (
        ('female', 'female'),
        ('male', 'male'),
        ('neutral', 'neutral'),
        ('undefined', 'undefined')
    )

    _id = models.ObjectIdField()

    uuid = models.BigIntegerField(default=make_id,
                                  unique=False,
                                  editable=False)

    # posted = models.TimeField(auto_now=True, help_text="last modified")
    posted = models.DateTimeField(auto_now=True, help_text="last modified")

    state = models.CharField(
        max_length=20,
        choices=STATES,
        default=1,  # default to draft
    )

    gender = models.CharField(max_length=15,
                              choices=GENDERS,
                              default='undefined')

    # ----- photos: before -----
    bf_img = ProcessedImageField(upload_to=get_bg_img_dir_name,
                                 processors=[ResizeToFill(1000, 750)],
                                 format='JPEG',
                                 options={'quality': 100},
                                 blank=True,
                                 null=True,
                                 help_text="before image")

    bf_img_cropped = ProcessedImageField(upload_to=get_bg_img_cropped_dir_name,
                                         # processors=[ResizeToFill(1000, 750)], // TODO: not sure
                                         format='JPEG',
                                         options={'quality': 100},
                                         blank=True,
                                         null=True,
                                         help_text="before image cropped")

    # 520:390,  4:3 X 130
    bf_img_thumb = ImageSpecField(source='bf_img_cropped',
                                  processors=[ResizeToFill(520, 390)],
                                  format='JPEG',
                                  options={'quality': 100})

    bf_cap = models.CharField(max_length=50,
                              default='',
                              blank=True,
                              help_text='before caption')

    # ----- photos: after -----
    af_img = ProcessedImageField(upload_to=get_af_img_dir_name,
                                 processors=[ResizeToFill(1000, 750)],
                                 format='JPEG',
                                 options={'quality': 100},
                                 blank=True,
                                 null=True,
                                 help_text="after image")

    af_img_cropped = ProcessedImageField(upload_to=get_af_img_cropped_dir_name,
                                         # processors=[ResizeToFill(1000, 750)],
                                         format='JPEG',
                                         options={'quality': 100},
                                         blank=True,
                                         null=True,
                                         help_text="before image cropped")

    af_img_thumb = ImageSpecField(source='af_img_cropped',
                                  processors=[ResizeToFill(520, 390)],
                                  format='JPEG',
                                  options={'quality': 100})

    af_cap = models.CharField(max_length=50,
                              default='',
                              blank=True,
                              help_text='after caption')

    # --------------------------

    is_official = models.BooleanField(default=False,
                                      blank=False,
                                      help_text='')

    pbm = models.BooleanField(default=False,
                              blank=True,
                              help_text='')

    title = models.CharField(max_length=30,
                             blank=True)

    pain_point = models.CharField(max_length=50,
                                  blank=True)

    rating = models.FloatField(help_text="ratings from google map API",
                               blank=True)

    ori_url = models.URLField(blank=True, help_text="source link")

    body = models.TextField(blank=True)

    # view_num = models.PositiveIntegerField(blank=True)

    # model_form_class = UserInfoForm
    author = models.EmbeddedModelField(
        model_container=UserInfo,
    )

    clinic = models.EmbeddedModelField(
        model_container=ClinicInfo
    )

    surgery_meta = models.EmbeddedModelField(
        model_container=SurgeryMeta,
        model_form_class=SurgeryMetaForm,
    )

    surgeries = models.ArrayModelField(
        model_container=SurgeryTag,
        model_form_class=SurgeryTagForm,
        default=[]
    )

    side_effects = models.ListField(blank=True,
                                    default=[],
                                    help_text="")

    view_num = models.PositiveIntegerField(default=0, help_text='number of views')

    def __str__(self):
        sig = ' '.join(['case', str(self.uuid)])
        sig = ' '.join([sig, self.title]) if self.title else sig
        return sig

    def indexing(self):
        """
        An indexing instance method that adds the object instance
        to the Elasticsearch index 'Cases' via the DocType.

        :return(obj): a case boj?
        """
        doc = CaseDoc(
            # meta={'id': self.id},
            title=self.title or '',
            is_official=self.is_official,
            id=str(self.uuid)  # uuid of case
        )
        doc.save()  # TODO, not sure, seems not need this.
        return doc.to_dict(include_meta=True)
