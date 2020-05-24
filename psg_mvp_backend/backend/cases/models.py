"""
Database models for cases

"""
from datetime import date

from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit
from djongo import models
from multiselectfield import MultiSelectField

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
    return '/'.join(['cases', 'case_' + str(instance.uuid), new_filename])  # TODO: tmp try


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


def get_scp_user_pic_dir_name(instance, filename):
    """
    Normalize the dir and file name of the scraped user img.
    :return(str): the relative dir path
    """
    extension = filename.split(".")[-1]
    new_filename = 'scp_user_pic.' + extension
    # obj.log.url, Media root is by default loaded
    return '/'.join(['cases', 'case_' + str(instance.uuid), new_filename])


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

    scp = models.BooleanField(default=False,
                              blank=True,
                              help_text='true if this case is scrapped.')

    scp_username = models.CharField(max_length=30,
                                    blank=True,
                                    help_text="scrapped username. Blank if the post is not scraped.")

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

    # doctor info
    # If doctor_profile_id is blank it means that the corresponding
    # DoctorProfile does not exist yet.
    doctor_name = models.CharField(max_length=30, blank=True)

    doctor_profile_id = models.CharField(max_length=40,
                                         blank=True,
                                         help_text="the _id field of DoctorProfile.")

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
        # all fields are not required
        for key, _ in self.fields.items():
            self.fields[key].required = False


class CaseImages(models.Model):
    """
    Concrete model for storing cases images other
    than before/after photos. TODO: WIP
    """
    # post = models.ForeignKey(Post, default=None)
    # image = models.ImageField(upload_to=get_image_filename,
    #                           verbose_name='Image')
    _id = models.ObjectIdField()

    # Image is resized to 120X120 pixels with django-imagekit
    # when you don't want to save the ori image
    img = ProcessedImageField(upload_to=get_case_dir_name,
                              processors=[ResizeToFit(height=970, upscale=False)],
                              format='JPEG',
                              options={'quality': 100},
                              blank=True,
                              null=True)

    img_thumb = ImageSpecField(source='img',
                               processors=[ResizeToFit(height=390, upscale=False)],
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
        ('', '')  # undefined
    )

    ANESTHESIA = (
        ('surface', '表面麻醉'),
        ('partial', '局部麻醉'),
        ('sleep', '睡眠麻醉'),
        ('tube', '插管全麻'),
        ('', '')  # undefined
    )

    POSITIVE_EXP_CHOICES = (('0', 'pre-surgery commu'),
                            ('1', 'risk commu'),
                            ('2', 'service'),
                            ('3', 'env'),
                            ('4', 'surgery effect'),
                            ('5', 'post-surgery tracking'))

    RECOVERY_CHOICES = (
        ('3d', '3 天'),
        ('1w', '1 week'),
        ('2w', '2 weeks'),
        ('1m', '1 month'),
        ('more', 'more'),
        ('', '')  # undefined
    )

    _id = models.ObjectIdField()

    uuid = models.BigIntegerField(default=make_id,
                                  unique=False,
                                  editable=False)

    # posted = models.TimeField(auto_now=True, help_text="last modified")
    posted = models.DateTimeField(auto_now=True, help_text="last modified")
    created = models.DateTimeField(auto_now_add=True, help_text="created")  # default=timezone.now

    state = models.CharField(
        max_length=20,
        choices=STATES,
        default=1,  # default to draft
    )

    gender = models.CharField(max_length=15,
                              choices=GENDERS,
                              default='undefined')

    recovery_time = models.CharField(max_length=20,
                                     choices=RECOVERY_CHOICES,
                                     default='undefined')

    # ----- photos: before -----
    bf_img = ProcessedImageField(upload_to=get_bg_img_dir_name,
                                 processors=[ResizeToFit(height=1000, upscale=False)],
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
                                 processors=[ResizeToFit(height=1000, upscale=False)],
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

    title = models.CharField(max_length=30,
                             blank=True)

    # pain_point = models.CharField(max_length=50,
    #                               blank=True)

    rating = models.FloatField(help_text="ratings from google map API",
                               blank=True)

    ori_url = models.URLField(blank=True, help_text="source link")

    body = models.TextField(blank=True)

    scp_user_pic = ProcessedImageField(upload_to=get_scp_user_pic_dir_name,
                                       processors=[ResizeToFill(100, 100)],
                                       format='JPEG',
                                       options={'quality': 100},
                                       blank=True,
                                       null=True,
                                       help_text='scrapped user profile pic')
    scp_user_pic_thumb = ImageSpecField(source='scp_user_pic',
                                        processors=[ResizeToFill(50, 50)],
                                        format='JPEG',
                                        options={'quality': 100})


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

    pain_points = models.ListField(blank=True,
                                   default=[],
                                   help_text="")

    anesthesia = models.CharField(
        max_length=20,
        choices=ANESTHESIA,
        default='undefined'
    )

    positive_exp = MultiSelectField(choices=POSITIVE_EXP_CHOICES,
                                    null=True, blank=True)

    view_num = models.PositiveIntegerField(default=0, help_text='number of views')

    # weird you can't set max value here
    interest = models.FloatField(default=0, blank=True)

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
            clinic_name=self.clinic.display_name or '',
            gender=self.gender,
            is_official=self.is_official,
            interest=self.interest,
            surgeries=[item.name for item in self.surgeries] if self.surgeries else [],
            id=str(self.uuid)  # uuid of case
        )

        # must add index, otherwise will get No Index error.
        doc.save(index="cases")  # TODO, not sure, seems not need this.
        return doc.to_dict(include_meta=True)
