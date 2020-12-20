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

    # for nested comments
    reply_to_id = models.CharField(default='',
                                   max_length=30,
                                   blank=True,
                                   help_text='id of its parent comment')

    # to avoid the need of fetching case again
    is_op = models.BooleanField(default=False,
                                blank=True,
                                help_text='is original author')

    def __str__(self):
        text_preview = '' if not self.text else self.text[:min(len(self.text), 10)]
        return '_'.join([self.case_id, text_preview])
