import factory

from cases.models import UserInfo
from comments.models import Comment


class CommentFactory(factory.django.DjangoModelFactory):
    """
    Factory class to create a sample comment object.
    """

    class Meta:
        model = Comment

    class Params:
        """
        Extra params that can be passed while initializing the object.
        """

        username = 'testuser'
        uuid = '1'

    text = 'testcomment'
    author = factory.LazyAttribute(lambda params: UserInfo(name=params.username, uuid=params.uuid))
