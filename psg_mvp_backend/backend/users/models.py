"""
Database models - User Model.

"""

from djongo import models
# from django_extensions.db.fields import ShortUUIDField
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from backend.shared.utils import make_id


class User(AbstractUser):
    """
    The sole User model extended from default Django User model.
    Four types of users in same db table:
    1) admin (built-in, is_staff is true)
    2) users (aka beauty seekers)
    3) doctor
    4) clinic

    """
    USER_TYPE_CHOICES = (
        ('user', 'user'),
        ('doctor', 'doctor'),
        ('clinic', 'clinic'),
    )

    GENDERS = (
        ('female', 'female'),
        ('male', 'male'),
        ('other', 'other'),
        ('', '')  # undefined
    )

    gender = models.CharField(max_length=15,
                              choices=GENDERS,
                              default='')

    _id = models.ObjectIdField()
    # TODO: might use this instead
    # uuid = ShortUUIDField()
    uuid = models.BigIntegerField(default=make_id,
                                  unique=True,
                                  editable=False)


    # override email as a required field
    # email = models.EmailField(_('email address'))
    user_type = models.CharField(max_length=10,
                                 choices=USER_TYPE_CHOICES,
                                 default=1)

    # many-to-one association w/ ClinicProfile model
    clinic_uuid = models.CharField(max_length=30,
                                   blank=True,
                                   help_text="the uuid field of ClinicProfile")


class RegistrationOTP(models.Model):
    _id = models.ObjectIdField()

    hashed_email = models.CharField(max_length=36,
                                 blank=False,
                                 editable=False,
                                 help_text="A md5 hash (32 chars) for email")

    otp = models.CharField(max_length=10,
                           blank=False,
                           editable=False,
                           help_text="6-digit verification code")

    created = models.DateTimeField(auto_now_add=True, help_text="created")  # default=timezone.now
