"""
Database models for reviews.

"""

from djongo import models
from django import forms
from multiselectfield import MultiSelectField


from backend.shared.utils import make_id
from cases.models import UserInfo, UserInfoForm, ClinicInfo, Case  # not so good dependency


############################################################
#   Djongo's Abstract Model
############################################################

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


class Review(models.Model):
    """
    DB model for Review (a.k.a., short case).

    """
    _id = models.ObjectIdField()
    uuid = models.BigIntegerField(default=make_id,
                                  unique=True,
                                  editable=False)

    # only used for scrapped reviews
    hash = models.CharField(max_length=20, null=True, blank=True, editable=False)

    posted = models.DateTimeField(auto_now=True, help_text="last modified")
    created = models.DateTimeField(auto_now_add=True, help_text="created")  # default=timezone.now

    scp_time = models.DateTimeField(null=True, blank=True, help_text="the time on the original post")

    # posted = models.TimeField(auto_now=True, help_text="last modified")
    author = models.EmbeddedModelField(
        model_container=UserInfo,
        model_form_class=UserInfoForm
    )

    body = models.TextField(blank=False)

    clinic = models.EmbeddedModelField(
        model_container=ClinicInfo
    )

    rating = models.FloatField(help_text="1 to 5", blank=True)

    # weird you can't set max value here
    interest = models.FloatField(default=0, blank=True)

    source = models.CharField(max_length=20, blank=True)

    positive_exp = MultiSelectField(choices=Case.POSITIVE_EXP_CHOICES,
                                    null=True, blank=True)

    doctors = models.ArrayModelField(
        model_container=Doctor,
        model_form_class=DoctorForm,
        default=[]
    )
