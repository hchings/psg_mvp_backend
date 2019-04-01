"""
Database models - User Model.

"""

from djongo import models
# from django_extensions.db.fields import ShortUUIDField
# from django.db import models
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
