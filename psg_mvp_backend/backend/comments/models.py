"""
Database models for comments.
Design guide: https://docs.mongodb.com/ecosystem/use-cases/storing-comments/

"""

from djongo import models

from backend.shared.utils import make_id
from cases.models import UserInfo, UserInfoForm


class Comment(models.Model):
    _id = models.ObjectIdField()
    uuid = models.BigIntegerField(default=make_id,
                                  unique=True,
                                  editable=False)

    case_id = models.CharField(max_length=30,
                               blank=False,
                               help_text="the uuid field in the corresponding case. Do not fill in this manually.")

    posted = models.DateTimeField(auto_now=True, help_text="last modified")
    # posted = models.TimeField(auto_now=True, help_text="last modified")
    author = models.EmbeddedModelField(
        model_container=UserInfo,
        model_form_class=UserInfoForm
    )

    text = models.TextField(blank=False)
