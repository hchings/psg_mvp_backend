"""
DRF Serializers for Reviews app.

"""
import coloredlogs, logging
from rest_framework import serializers, exceptions
from annoying.functions import get_object_or_None

from django.contrib.auth import get_user_model

from cases.models import UserInfo, ClinicInfo
from cases.serializers import ClinicInfoSerializer
from users.clinics.models import ClinicProfile
from backend.shared.serializers import AuthorSerializer, PartialAuthorSerializer
from backend.shared.fields import embedded_model_method
from backend.settings import ROOT_URL
from .models import Review

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

user_mode = get_user_model()

# The better way is to transform items in frontend.
# This is used as a hack bcz algolia transformItems
# is broken and will be fired multiple times.
TOPICS_MAPPING = {
    'consult': '諮詢',
    'env': '環境',
    'price': '性價比',
    'service': '服務',
    'skill': '醫術'
}


class ReviewSerializer(serializers.ModelSerializer):
    uuid = serializers.ReadOnlyField()
    topics = serializers.SerializerMethodField(required=False)
    services = serializers.SerializerMethodField(required=False)
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Review
        fields = ('uuid', 'created', 'rating', 'author', 'body', 'services', 'topics', 'consult_only', 'verify_pic',
                  'scp_time', 'scp_user_pic', 'source')

    def __init__(self, *args, **kwargs):
        # to include Algolia-specific fields
        self.indexing_algolia = kwargs.get("indexing_algolia", False)

        if self.indexing_algolia:
            # downstream can't accept this keyword
            kwargs.pop('indexing_algolia')
            # for ranking purpose (scp and organic posts have timestamp in the same field)
            self.fields['scp_time'] = serializers.SerializerMethodField()

        super(ReviewSerializer, self).__init__(*args, **kwargs)

        try:
            if 'request' in self.context:
                if self.context['request'].method in ['GET']:
                    self.fields['author'] = PartialAuthorSerializer()
                else:
                    # review list is query by clinic uuid, so we don't need it in response
                    # self.fields['clinic'] = ClinicInfoSerializer(required=True)
                    self.fields['clinic'] = serializers.CharField(required=True)
                    self.fields['verify_pic'] = serializers.ImageField(max_length=None,
                                                                       use_url=True,
                                                                       required=False)
            if self.indexing_algolia:
                self.fields['objectID'] = serializers.SerializerMethodField(required=False)
                self.fields['author'] = PartialAuthorSerializer()
                self.fields['clinic'] = ClinicInfoSerializer(required=False)

            if not self.context.get('request', None):
                self.fields['scp_user_pic'] = serializers.SerializerMethodField()
                self.fields['verify_pic'] = serializers.SerializerMethodField()


        except KeyError as e:
            logger.error("[ReviewSerializer] %s" % str(e))

    def create(self, validated_data):
        """
        Need to pop any embeddedmodel field of djongo and create the abstract
        item by ourselves.
        More info: https://github.com/nesdis/djongo/issues/238

        :param validated_data:
        :return:
        """
        author = self.context['request'].user

        clinic_display_name = validated_data.pop('clinic')

        # link to clinic, branch, and doctors
        clinic_obj = get_object_or_None(ClinicProfile, display_name=clinic_display_name)

        if clinic_obj is None:
            logger.warning("[Create Review]: Can't find clinic %s" % clinic_display_name)
            review_obj = Review.objects.create(**validated_data,
                                               author=UserInfo(name=author.username,
                                                               uuid=author.uuid),
                                               clinic=ClinicInfo(display_name=clinic_display_name))
        else:
            review_obj = Review.objects.create(**validated_data,
                                               author=UserInfo(name=author.username,
                                                               uuid=author.uuid),
                                               clinic=ClinicInfo(display_name=clinic_obj.display_name,
                                                                 uuid=clinic_obj.uuid))

        return review_obj

    def get_objectID(self, obj):
        return str(obj.uuid)

    def get_services(self, obj):
        return obj.services or []

    def get_topics(self, obj):
        """
        To serialize ArrayModelField from djongo.
        :param obj:
        :return:
        """
        return embedded_model_method(obj,
                                     self.Meta.model,
                                     'topics',
                                     included_fields=['topic'],
                                     value_mapping=TOPICS_MAPPING)

    def get_scp_user_pic(self, obj):
        return "" if not obj.scp_user_pic else ROOT_URL + obj.scp_user_pic.url

    def get_verify_pic(self, obj):
        return "" if not obj.verify_pic else ROOT_URL + obj.verify_pic.url

    def get_scp_time(self, obj):
        if obj.scp_time:
            return str(obj.scp_time)
        else:
            return str(obj.created)
    # def get_like_num(self, obj):
    #     """
    #
    #     :param obj:
    #     :return:
    #     """
    #
    #     # TODO: WIP
    #     return 0

    # def get_liked_by_user(self, obj):
    #     """
    #     Return a boolean flag indicating whether the user
    #     in the request liked the current comment.
    #
    #     For unauthorized users, it will always be false.
    #
    #     :param obj: the comment object
    #     :return (boolean):
    #     """
    #     # TODO: WIP. not getting context
    #     # request = self.context.get('request', None)
    #     #
    #     # if request:
    #     #     # note that this might return an AnonymousUser
    #     #     user = request.user
    #     #     # logger.info("got user", user)
    #     #
    #     #     if not user.is_anonymous:
    #     #         # each comment at most have two two activity stream objects (one like and one unlike)
    #     #         # from each user. This is to reduce the unnecessary space used in db.
    #     #         # Put the more recent activity on the type with order_by.
    #     #         action_objs = obj.action_object_actions.filter(actor_object_id=user._id).order_by('-timestamp')
    #     #         logger.info("action_objs in serializer %s" % action_objs)
    #     #
    #     #         if not action_objs:
    #     #             return False
    #     #
    #     #         return False if not action_objs or action_objs[0].verb == 'unlike' else True
    #
    #     # for unlogin user
    #     return False
