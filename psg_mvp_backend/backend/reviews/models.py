"""
Database models for reviews (short case).

"""
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill, ResizeToFit

from djongo import models
from django import forms
from multiselectfield import MultiSelectField

from backend.shared.utils import make_id
from cases.models import UserInfo, UserInfoForm, ClinicInfo, Case  # not so good dependency


def get_scp_user_pic_dir_name(instance, filename):
    """
    Normalize the dir and file name of the scraped user img.
    :return(str): the relative dir path
    """
    extension = filename.split(".")[-1]
    new_filename = 'scp_user_pic.' + extension
    return '/'.join(['reviews', 'review_' + str(instance.uuid), new_filename])


def get_verify_pic_dir_name(instance, filename):
    """
    Normalize the dir and file name of the scraped user img.
    :return(str): the relative dir path
    """
    extension = filename.split(".")[-1]
    new_filename = 'verify_pic.' + extension
    return '/'.join(['reviews', 'review_' + str(instance.uuid), filename])


########################################
#   Djongo's Abstract Model -- Doctor
########################################

class Doctor(models.Model):
    """
    Abstract model representing the info of a doctor.
    Many-to-one relationship to Review.
    """

    class Meta:
        abstract = True

    name = models.CharField(max_length=30, blank=True, help_text="doctor name")

    profile_id = models.CharField(max_length=40,
                                  blank=True,
                                  help_text="the _id field of DoctorProfile.")

    # must implement this
    def __str__(self):
        return '%s (%s)' % (self.name, self.profile_id) if self.profile_id else self.name


class DoctorForm(forms.ModelForm):
    """
    Customize form for SurgeryTag from djongo bcz
    the self-generated Form has all fields set to required.
    """

    class Meta:
        model = Doctor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DoctorForm, self).__init__(*args, **kwargs)
        # all fields are not required except for branch_name
        for key, _ in self.fields.items():
            self.fields[key].required = False


########################################
#              Review Models
########################################

class ReviewTopic(models.Model):
    """
    Abstract model representing the info of a review topic.
    one-to-many relationship to Review.
    """

    class Meta:
        abstract = True

    REVIEW_TOPICS = (
        ('consult', 'consult'),
        ('env', 'env'),
        ('price', 'price'),
        ('service', 'service'),
        ('skill', 'skill'),
    )

    # SENTIMENTS = (
    #     (-1, -1), # negative
    #     (0, 0), # neutral
    #     (1, 1) # positive
    # )

    topic = models.CharField(max_length=20,
                             choices=REVIEW_TOPICS,
                             null=False,
                             blank=False)
    sentiment = models.IntegerField(default=0,
                                    null=True,
                                    blank=True)

    def __str__(self):
        return "%s (%s)" % (self.topic, self.sentiment) if self.sentiment is not None \
            else self.topic


class ReviewTopicForm(forms.ModelForm):
    """
    Customize form for SurgeryTag from djongo bcz
    the self-generated Form has all fields set to required.
    """

    class Meta:
        model = ReviewTopic
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ReviewTopicForm, self).__init__(*args, **kwargs)
        # all fields are not required except for branch_name
        for key, _ in self.fields.items():
            self.fields[key].required = False


class Review(models.Model):
    """
    DB model for Review (a.k.a., short case).

    """
    STATES = (
        ('hidden', 'hidden'),
        ('is_spam', 'is_spam'),
        ('reviewing', 'reviewing'),
        ('published', 'published'),
    )

    SCRAP_SOURCES = (
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('', ''),
    )

    _id = models.ObjectIdField()
    uuid = models.BigIntegerField(default=make_id,
                                  unique=True,
                                  editable=False)
    state = models.CharField(
        max_length=20,
        choices=STATES,
        default='published',  # default to published
    )

    posted = models.DateTimeField(auto_now=True, help_text="last modified")
    created = models.DateTimeField(auto_now_add=True, help_text="created")  # default=timezone.now
    rating = models.PositiveIntegerField(help_text="1 to 5", blank=True)

    body = models.TextField(blank=False)

    author = models.EmbeddedModelField(
        model_container=UserInfo,
        model_form_class=UserInfoForm
    )
    clinic = models.EmbeddedModelField(
        model_container=ClinicInfo
    )
    doctors = models.ArrayModelField(
        model_container=Doctor,
        model_form_class=DoctorForm,
        default=[],
        blank=True,
        null=True
    )

    consult_only = models.BooleanField(default=False,
                                       blank=True,
                                       help_text='only have consultation')

    # limit to one img for now
    verify_pic = ProcessedImageField(upload_to=get_verify_pic_dir_name,
                                     processors=[ResizeToFit(height=500, upscale=False)],
                                     format='JPEG',
                                     options={'quality': 100},
                                     blank=True,
                                     null=True,
                                     help_text='a picture to proof that you received the service.')

    # =================================
    #                NLP
    # =================================
    # TODO: should this be Service Tag?
    services = models.ListField(blank=True,
                                default=[],
                                help_text="")

    topics = models.ArrayModelField(
        model_container=ReviewTopic,
        model_form_class=ReviewTopicForm,
        default=[],
        # blank=True,
        # null=True
    )

    # =================================
    #   Only used for scrapped review
    # =================================
    source = MultiSelectField(choices=SCRAP_SOURCES,
                              default='',
                              null=True,
                              blank=True)
    hash = models.CharField(max_length=20, null=True, blank=True, editable=False)
    scp_time = models.DateTimeField(null=True, blank=True, help_text="the time on the original post")
    scp_user_pic = ProcessedImageField(upload_to=get_scp_user_pic_dir_name,
                                       processors=[ResizeToFill(60, 60)],
                                       format='JPEG',
                                       options={'quality': 100},
                                       blank=True,
                                       null=True,
                                       help_text='scrapped user profile pic')

    def __str__(self):
        text_preview = '' if not self.body else self.body[:min(len(self.body), 6)]
        return '_'.join([self.clinic.display_name, text_preview])
