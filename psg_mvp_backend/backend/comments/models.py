"""
Database models for comments.
Design guide: https://docs.mongodb.com/ecosystem/use-cases/storing-comments/

"""

from djongo import models

from cases.models import UserInfo, UserInfoForm


class Comment(models.Model):
    _id = models.ObjectIdField()
    case_id = models.CharField(max_length=30,
                               blank=False,
                               help_text="the uuid field in the corresponding case. Do not fill in this manually.")

    posted = models.TimeField(auto_now=True, help_text="last modified")
    author = models.EmbeddedModelField(
        model_container=UserInfo,
        model_form_class=UserInfoForm
    )

    text = models.TextField(blank=False)
