import factory

from cases.models import UserInfo
from comments.models import Comment


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    class Params:
        username = 'testuser'
        uuid = '1'

    text = 'testcomment'
    author = factory.LazyAttribute(lambda params: UserInfo(name=params.username, uuid=params.uuid))
