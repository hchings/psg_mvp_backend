"""
DRF Serializers for Comments app.

"""
import coloredlogs, logging
from rest_framework import serializers, exceptions
from django.contrib.auth import get_user_model

from cases.models import UserInfo
from backend.shared.serializers import AuthorSerializer, PartialAuthorSerializer
# from cases.serializers import AuthorSerializer
from .models import Comment


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

user_mode = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    # author = serializers.SerializerMethodField()
    author = AuthorSerializer()
    uuid = serializers.ReadOnlyField()
    like_num = serializers.SerializerMethodField(required=False)
    # liked by current user
    liked_by_user = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Comment
        fields = ('case_id', 'uuid', 'posted', 'author', 'like_num', 'liked_by_user', 'text')

    def __init__(self, *args, **kwargs):
        super(CommentSerializer, self).__init__(*args, **kwargs)

        try:
            if self.context['request'].method in ['GET']:
                self.fields['author'] = PartialAuthorSerializer()
            else:
                self.fields['author'] = AuthorSerializer()
        except KeyError:
            pass

    def create(self, validated_data):
        """
        Need to pop any embeddedmodel field of djongo and create the abstract
        item by ourselves.
        More info: https://github.com/nesdis/djongo/issues/238

        :param validated_data:
        :return:
        """
        # print("validated data", validated_data)
        author = validated_data.pop('author')
        case_obj = Comment.objects.create(**validated_data,
                                          author=UserInfo(name=author.get('name', ''),
                                                          uuid=author.get('uuid', '')))
        return case_obj

    def get_like_num(self, obj):
        """
        # TODO: this is wrong
        :param obj:
        :return:
        """
        return len(obj.action_object_actions.filter(verb='like'))

    def get_liked_by_user(self, obj):
        """
        Return a boolean flag indicating whether the user
        in the request liked the current comment.

        For unauthorized users, it will always be false.

        :param obj: the comment object
        :return (boolean):
        """
        # TODO: not getting context
        request = self.context.get('request', None)

        if request:
            # note that this might return an AnonymousUser
            user = request.user
            # logger.info("got user", user)

            if not user.is_anonymous:
                action_objs = obj.action_object_actions.filter(actor_object_id=user._id, verb="like")
                # logger.info("action_objs in serializer %s" % action_objs)
                return False if not action_objs else True

        # for unlogin user
        return False
