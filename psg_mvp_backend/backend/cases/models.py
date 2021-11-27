"""
Database models for cases

"""
from datetime import date

from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit
from djongo import models
from multiselectfield import MultiSelectField
from hitcount.models import HitCountMixin, HitCount
from hitcount.managers import HitCountManager, HitManager
from annoying.functions import get_object_or_None

from uuid import uuid4

from django import forms
# from users.clinics.models import ClinicProfile
from backend.settings import ROOT_URL
from backend.shared.utils import _prep_catalog, make_id, get_category

YEAR_CHOICES = [(y, y) for y in range(2000, date.today().year + 1)]
MONTH_CHOICE = [(m, m) for m in range(1, 13)]

_, sub_cate_to_cate = _prep_catalog()


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
    return '/'.join(['cases', 'case_' + str(instance.uuid), new_filename])  # TODO: tmp try


def get_bg_img_cropped_dir_name(instance, filename):
    """
    Normalize the dir and file name of the cropped before img.
    :return(str): the relative dir path
    """
    extension = filename.split(".")[-1]
    new_filename = 'before_cropped.' + extension
    return '/'.join(['cases', 'case_' + str(instance.uuid), new_filename])


def get_af_img_dir_name(instance, filename):
    """
    Normalize the dir and file name of the after img.
    :return(str): the relative dir path
    """
    extension = filename.split(".")[-1]
    new_filename = 'after.' + extension
    return '/'.join(['cases', 'case_' + str(instance.uuid), new_filename])


def get_af_img_cropped_dir_name(instance, filename):
    """
    Normalize the dir and file name of the cropped after img.
    :return(str): the relative dir path
    """
    extension = filename.split(".")[-1]
    new_filename = 'after_cropped.' + extension
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

    display_name = models.CharField(max_length=30, blank=True)  # TODO
    branch_name = models.CharField(max_length=20, blank=True)

    # to get branch name
    place_id = models.CharField(max_length=50,
                                blank=True,
                                help_text="unique google place_id")
    # editable = False,
    uuid = models.CharField(max_length=30,
                            blank=True,
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


class ClinicInfoForm(forms.ModelForm):
    """
    Customize form for SurgeryMeta from djongo bcz
    the self-generated Form has all fields set to required.
    """

    class Meta:
        model = ClinicInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ClinicInfoForm, self).__init__(*args, **kwargs)
        # all fields are not required
        for key, _ in self.fields.items():
            self.fields[key].required = False


class SurgeryMeta(models.Model):
    """
    Abstract model representing the meta info of a Case.
    one-to-one relationship to Case.
    """

    class Meta:
        abstract = True

    year = models.IntegerField(choices=YEAR_CHOICES, null=True)
    month = models.IntegerField(choices=MONTH_CHOICE, null=True)
    min_price = models.PositiveIntegerField(blank=True, null=True)
    max_price = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        # tmp
        return str(self.year)


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
    than before/after photos.
    """
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

    case_uuid = models.CharField(max_length=30,
                                 blank=False,
                                 unique=False,
                                 help_text="the uuid field in the corresponding case. Do not fill in this manually.")

    order = models.IntegerField(null=False,
                                blank=False,
                                default=0,
                                help_text='image order. 0 first')

    def __str__(self):
        return str(self.img) if self.order is None else str(self.img) + ' (%s)' % self.order


class Case(models.Model, HitCountMixin):
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
        ('others', 'others'),
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

    SKIP_REASONS = (
        ('dissent', 'dissent from author'),
        ('quality', 'low quality'),
        ('rules', 'violate community rules'),
        ('', '')  # undefined
    )

    _id = models.ObjectIdField()

    uuid = models.BigIntegerField(default=make_id,
                                  unique=True,
                                  editable=False)

    # not working, Djongo/mongo does not support relation
    # hit_count = GenericRelation(HitCount, object_id_field='object_uuid',
    #                             related_query_name='hit_count_generic_relation')
    posted = models.DateTimeField(auto_now=True, help_text="the real value of last modified")
    author_posted = models.DateTimeField(blank=True,
                                         null=True,
                                         help_text="the real value of last modified")
    created = models.DateTimeField(auto_now_add=True, help_text="created")  # default=timezone.now

    state = models.CharField(
        max_length=20,
        choices=STATES,
        default=1,  # default to reviewing
    )

    gender = models.CharField(max_length=15,
                              choices=GENDERS,
                              default='female')

    case_number = models.CharField(max_length=30,
                                   blank=True,
                                   null=True,
                                   help_text="customized case number by clinics")

    recovery_time = models.CharField(max_length=20,
                                     blank=True,
                                     null=True,
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
                                         format='JPEG',
                                         options={'quality': 100},
                                         blank=True,
                                         null=True,
                                         help_text="before image cropped")

    # 520:390, 4:3 X 130
    bf_img_thumb = ImageSpecField(source='bf_img_cropped',
                                  processors=[ResizeToFill(520, 390)],
                                  format='JPEG',
                                  options={'quality': 100})

    bf_cap = models.CharField(max_length=200,
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
                                         format='JPEG',
                                         options={'quality': 100},
                                         blank=True,
                                         null=True,
                                         help_text="before image cropped")

    af_img_thumb = ImageSpecField(source='af_img_cropped',
                                  processors=[ResizeToFill(520, 390)],
                                  format='JPEG',
                                  options={'quality': 100})

    af_cap = models.CharField(max_length=200,
                              default='',
                              blank=True,
                              help_text='after caption')

    # --------------------------

    is_official = models.BooleanField(default=False,
                                      blank=False,
                                      help_text='')

    # false or none means it's a successful case
    failed = models.BooleanField(default=False,
                                 blank=True,
                                 help_text='set to true if this case is a failed surgery')

    title = models.CharField(max_length=100,
                             blank=True)

    rating = models.FloatField(help_text="ratings from google map API",
                               blank=True)

    ori_url = models.URLField(blank=True, help_text="source link", max_length=1000)

    body = models.TextField(blank=True)

    consent = models.BooleanField(default=False,
                                  blank=True,
                                  help_text='if a case is scraped, whether it got the consent from the author')

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

    author = models.EmbeddedModelField(
        model_container=UserInfo,
    )

    clinic = models.EmbeddedModelField(
        model_container=ClinicInfo,
        model_form_class=ClinicInfoForm,
        blank=True,
        null=True
    )

    surgery_meta = models.EmbeddedModelField(
        model_container=SurgeryMeta,
        model_form_class=SurgeryMetaForm,
        blank=True,
        null=True
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
        default='undefined',
        blank=True
    )

    positive_exp = MultiSelectField(choices=POSITIVE_EXP_CHOICES,
                                    null=True, blank=True)

    age = models.PositiveIntegerField(blank=True, null=True)

    interest = models.FloatField(default=0, blank=True)

    # case management
    skip = models.BooleanField(default=False,
                               help_text='set to true to hide case from any UIs')

    skip_reason = models.CharField(
        max_length=30,
        choices=SKIP_REASONS,
        default='',
        blank=True,
        null=True
    )

    def __str__(self):
        sig = ' '.join(['case', str(self.uuid)])
        sig = ' '.join([sig, self.title]) if self.title else sig
        return sig

    def indexing(self, root_url="", included_fields=[]):
        """
        An indexing instance method that adds the object instance
        to the Algolia's index.

        :return(dict): the case object in dict form.
        """
        # clinic_obj = get_object_or_None(ClinicProfile, uuid=self.clinic.uuid)


        obj = {
            "objectID": self.uuid,
            "uuid": self.uuid,
            "title": self.title or '',
            "clinic": {
                "display_name": self.clinic.display_name or '',
                "uuid": self.clinic.uuid,
            },
            "type": [get_category(surgery_obj.get('name', 'ERR')) for surgery_obj in self.surgeries
                           if get_category(surgery_obj.get('name', 'ERR'))],
            "failed": self.failed,
            "is_official": self.is_official,
            "surgeries": [{"name": item.name} for item in self.surgeries],
            "af_img_thumb": (root_url or ROOT_URL) + self.af_img_thumb.url,
            "bf_img_thumb": (root_url or ROOT_URL) + self.bf_img_thumb.url,
            # "logo": (root_url or ROOT_URL) + clinic_obj.logo_thumbnail_small.url,
            "posted": self.author_posted or self.posted,
            "interest": self.interest,
            "author": self.author.scp_username if self.author.scp else self.author.name,
        }

        if included_fields:
            obj_new = {
                "objectID": obj["objectID"]
            }
            for field in included_fields:
                obj_new[field] = obj[field]
            obj = obj_new

        return obj


############################################################
#     Invite to write case tokens
#     For now, each user will only have one referral code
#############################################################

class CaseInviteToken(models.Model):
    _id = models.ObjectIdField()

    token = models.UUIDField(primary_key=False,
                             default=uuid4,
                             editable=False)

    user_code = models.CharField(max_length=30,
                                 unique=False,
                                 editable=False,
                                 help_text="")

    user_uuid = models.CharField(max_length=30,
                                 unique=False,
                                 editable=False,
                                 help_text="the uuid field in the corresponding user. Do not fill in this manually.")

    created_at = models.DateTimeField(auto_now_add=True)


############################################################
#     Hit Count. See Hit Count package for code details.
#
#############################################################

class Hit(models.Model):
    """
    Model captures a single Hit by a visitor.
    None of the fields are editable because they are all dynamically created.
    Browsing the Hit list in the Admin will allow one to blacklist both
    IP addresses as well as User Agents. Blacklisting simply causes those
    hits to not be counted or recorded.
    Depending on how long you set the HITCOUNT_KEEP_HIT_ACTIVE, and how long
    you want to be able to use `HitCount.hits_in_last(days=30)` you can choose
    to clean up your Hit table by using the management `hitcount_cleanup`
    management command.
    """
    created = models.DateTimeField(editable=False, auto_now_add=True, db_index=True)
    ip = models.CharField(max_length=40, editable=False, db_index=True)
    session = models.CharField(max_length=40, editable=False, db_index=True)
    user_agent = models.CharField(max_length=255, editable=False)
    user = models.CharField(max_length=40, editable=False, blank=False)  # user Uuid
    hitcount = models.CharField(max_length=40, blank=False)  # hitcount pk

    objects = HitManager()

    class Meta:
        ordering = ('-created',)
        get_latest_by = 'created'

    def __str__(self):
        return 'Hit: %s' % self.pk

    def save(self, *args, **kwargs):
        """
        The first time the object is created and saved, we increment
        the associated HitCount object by one. The opposite applies
        if the Hit is deleted.
        """
        if self.pk is None:
            # get hitcount object and increase
            try:
                # print("fined pk", self.hitcount)
                hitcount_obj = HitCount.objects.get(pk=str(self.hitcount))
                if hitcount_obj.hits is None:
                    hitcount_obj.hits = 1
                else:
                    hitcount_obj.hits = hitcount_obj.hits + 1
                    hitcount_obj.save()
            except Exception as e:
                print("Hit error: no obj", e)

        super(Hit, self).save(*args, **kwargs)
