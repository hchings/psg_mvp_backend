"""
Database models for doctors

"""
import os

from djongo import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from django import forms
from django.conf import settings


def get_doctor_base_path(instance):
    return os.path.join(settings.MEDIA_ROOT, '/'.join(['doctors', 'doctor_' + str(instance.uuid)]))


def get_doctor_dir_name(instance, filename):
    base_path = get_doctor_base_path(instance)
    extension = filename.split(".")[-1]
    new_filename = 'profile.' + extension
    return os.path.join(base_path, new_filename)


def get_background_item_dir_name(instance, filename):
    pass
    # base_path = get_doctor_base_path(instance)
    # extension = filename.split(".")[-1]
    # new_filename = '.'.join(instance.extension)
    # return os.path.join(settings.MEDIA_ROOT,
    #                     '/'.join(['doctors']))


class BackgroundItem(models.Model):
    """
    Abstract model representing the info of
    a certificate/working exp/educational background, etc.
    """
    class Meta:
        abstract = True

    item = models.CharField(max_length=50, blank=False, help_text="item name")
    start_year = models.PositiveIntegerField(blank=True)
    end_year = models.PositiveIntegerField(blank=True)
    # TODO: e.g., for degree, can normalize them and put an icon.
    # TODO: skip for now.
    photo = ProcessedImageField(upload_to=get_background_item_dir_name,
                                processors=[ResizeToFill(180, 235, upscale=False)],
                                format='JPEG',
                                options={'quality': 100},
                                blank=True,
                                null=True,
                                help_text="Do not use it yet.")

    def __str__(self):
        return self.item


class BackgroundItemForm(forms.ModelForm):
    """
    Customize form for ArrayModelField from djongo bcz
    the self-generated Form has all fields set to required.
    """
    class Meta:
        model = BackgroundItem
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BackgroundItemForm, self).__init__(*args, **kwargs)
        # all fields are not required except for item
        for key, _ in self.fields.items():
            if key not in ['item']:
                self.fields[key].required = False


class DoctorProfile(models.Model):
    """
    Doctor Profile model.
    One-on-one relationship to User model (user_type='doctor').

    Many-to-one relationship to ClinicProfile.
        - The reference is put at DoctorProfile side.
        - The reference is the display_name in the ClinicProfile

    Pattern Reference:
        https://docs.mongodb.com/manual/tutorial/model-referenced-one-to-many-relationships-between-documents/

    """

    _id = models.ObjectIdField()

    # ---fields copy from the User colleciton ---
    user_id = models.CharField(max_length=30,
                               blank=False,
                               editable=False,
                               help_text="the _id field of the User collection. Do not fill in this manually.")

    uuid = models.CharField(max_length=30,
                            unique=True,  # TODO: unsure
                            editable=False,
                            help_text="the uuid field in the corresponding user. Do not fill in this manually.")

    display_name = models.CharField(max_length=30, blank=False, help_text="doctor name")

    # --- many-to-one relationship to ClinicProfile ----
    # a safer option
    clinic_uuid = models.CharField(max_length=30,
                                   blank=False,
                                   editable=True,
                                   help_text="the uuid field of the Clinic user collection. \
                                                Do not fill in this manually.")

    # need this for brief card view
    clinic_name = models.CharField(max_length=30,
                                   blank=True,
                                   help_text="reference key to ClinicProfile (the 'display_name' field).")

    # -------------------------------------------

    position = models.CharField(max_length=30,
                                default='',
                                blank=True,
                                help_text='position name in the clinic')

    is_primary = models.BooleanField(default=False,
                                     blank=True,
                                     help_text='the core doctor in that clinic')

    relevant = models.BooleanField(default=True,
                                   blank=False,
                                   help_text='set to true if the doctor is relevant to cosmetic/plastic surgery')

    english_name = models.CharField(max_length=30,
                                    default='',
                                    blank=True,
                                    help_text='english username')

    nick_name = models.CharField(max_length=30,
                                 default='',
                                 blank=True,
                                 help_text='marketing nick name')

    # Image is resized to 180X180 pixels with django-imagekit
    profile_photo = ProcessedImageField(upload_to=get_doctor_dir_name,
                                        processors=[ResizeToFill(180, 235, upscale=False)],
                                        format='JPEG',
                                        options={'quality': 100},
                                        blank=True,
                                        null=True)

    # detailed info
    bio = models.TextField(blank=True, help_text="1-2 paragraphs for bio")
    degrees = models.ArrayModelField(
        model_container=BackgroundItem,
        model_form_class=BackgroundItemForm,
        default=[],
        blank=True
    )

    certificates = models.ArrayModelField(
        model_container=BackgroundItem,
        model_form_class=BackgroundItemForm,
        default=[],
        blank=True
    )

    work_exps = models.ArrayModelField(
        model_container=BackgroundItem,
        model_form_class=BackgroundItemForm,
        default=[],
        blank=True,
        help_text="working experience"
    )

    other_exps = models.ArrayModelField(
        model_container=BackgroundItem,
        model_form_class=BackgroundItemForm,
        default=[],
        blank=True,
        help_text="miscellaneous other experience"
    )

    # postgre version
    # certificates = ArrayField(models.CharField(max_length=80, default=list, blank=True), blank=True, null=True)

    # TODO: this is not and should not be used as taggings.
    # TODO: Just a tmp way to store down the info from official sites
    professions_raw = models.ListField(blank=True,
                                       default=[],
                                       help_text="the original professions on official sites w/out any normalization")

    youtube_url = models.URLField(blank=True, help_text="any intro video")
    blog_url = models.URLField(blank=True, help_text="personal blog")
    fb_url = models.URLField(blank=True, help_text="personal fb page")

    # --- for internal user only ---
    first_check = models.BooleanField(default=False, blank=True, help_text="first manual data checking")

    def __str__(self):
        """
        Adding a clinic name behind for
        the convenience of backward lookup on clinics.

        """
        return '%s_%s' % (self.clinic_name, self.display_name)
