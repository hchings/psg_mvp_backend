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
from users.doctors.models import DoctorProfile
from backend.shared.serializers import AuthorSerializer, PartialAuthorSerializer
from backend.shared.fields import embedded_model_method
# from cases.serializers import AuthorSerializer
from .models import Review, Doctor

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

user_mode = get_user_model()


# class ClinicInfoSerializer(serializers.Serializer):
#     """
#     Serializer for clinic field.
#     """
#     display_name = serializers.CharField()
#     branch_name = serializers.CharField(required=False, allow_blank=True)
#     # doctor_name = serializers.CharField(required=False, allow_blank=True)
#     place_id = serializers.ReadOnlyField()
#     uuid = serializers.ReadOnlyField()


class ReviewSerializer(serializers.ModelSerializer):
    # author = serializers.SerializerMethodField()
    author = AuthorSerializer()
    uuid = serializers.ReadOnlyField()
    doctors = serializers.SerializerMethodField(required=False)
    positive_exp = serializers.ListField(required=False)

    # clinic = ClinicInfoSerializer(required=False)
    like_num = serializers.SerializerMethodField(required=False)
    # liked by current user
    liked_by_user = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Review
        fields = ('uuid', 'created', 'scp_time', 'rating', 'source', 'author', 'like_num',
                  'liked_by_user', 'body', 'doctors', 'positive_exp')

    def __init__(self, *args, **kwargs):
        super(ReviewSerializer, self).__init__(*args, **kwargs)

        try:
            if self.context['request'].method in ['GET']:
                self.fields['author'] = PartialAuthorSerializer()
            else:
                self.fields['author'] = AuthorSerializer()
                # review list is query by clinic uuid, so we don't need it in response
                self.fields['clinic'] = ClinicInfoSerializer(required=False)
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

        # ordereddict
        author = validated_data.pop('author')
        clinic = validated_data.pop('clinic')

        # link to clinic, branch, and doctors
        clinic_obj = get_object_or_None(ClinicProfile, display_name=clinic['display_name']) or {}
        branch_obj = {}
        if 'branch_name' in clinic:
            for branch in clinic_obj.branches or []:
                if branch.branch_name == clinic['branch_name']:
                    branch_obj = branch
                    break

        if not clinic:
            logger.warning("[Create Review]: Can't find clinic %s" % clinic['display_name'])

        if not branch_obj:
            logger.warning("[Create Review]: Can't find branch obj %s" % clinic.get('branch_name', ''))

        doctors = []
        if 'doctor_name' in clinic:
            doctor_obj = get_object_or_None(DoctorProfile,
                                            clinic_name=clinic['display_name'],
                                            display_name=clinic.get('doctor_name', ''))
            if doctor_obj:
                doctors.append(Doctor(name=doctor_obj.display_name,
                                      profile_id=str(doctor_obj._id)))

        review_obj = Review.objects.create(**validated_data,
                                           author=UserInfo(name=author.get('name', ''),
                                                           uuid=author.get('uuid', '')),
                                           clinic=ClinicInfo(display_name=clinic_obj.display_name,
                                                             branch_name=branch_obj.branch_name,
                                                             place_id=branch_obj.place_id),
                                           doctors=doctors)
        return review_obj

    # TODO: we might not need profile_id of doctors
    def get_doctors(self, obj):
        """
        To serialize ArrayModelField doctors from djongo.
        :param obj:
        :return:
        """
        return embedded_model_method(obj, self.Meta.model, 'doctors')

    def get_like_num(self, obj):
        """

        :param obj:
        :return:
        """

        # TODO: WIP
        return 0

    def get_liked_by_user(self, obj):
        """
        Return a boolean flag indicating whether the user
        in the request liked the current comment.

        For unauthorized users, it will always be false.

        :param obj: the comment object
        :return (boolean):
        """
        # TODO: WIP. not getting context
        # request = self.context.get('request', None)
        #
        # if request:
        #     # note that this might return an AnonymousUser
        #     user = request.user
        #     # logger.info("got user", user)
        #
        #     if not user.is_anonymous:
        #         # each comment at most have two two activity stream objects (one like and one unlike)
        #         # from each user. This is to reduce the unnecessary space used in db.
        #         # Put the more recent activity on the type with order_by.
        #         action_objs = obj.action_object_actions.filter(actor_object_id=user._id).order_by('-timestamp')
        #         logger.info("action_objs in serializer %s" % action_objs)
        #
        #         if not action_objs:
        #             return False
        #
        #         return False if not action_objs or action_objs[0].verb == 'unlike' else True

        # for unlogin user
        return False
