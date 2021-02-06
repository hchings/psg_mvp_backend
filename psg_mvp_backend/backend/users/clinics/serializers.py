"""
DRF Serializers for clinics.

"""

import ast
from random import randint

from rest_framework import serializers, exceptions
# from rest_auth.registration.serializers import RegisterSerializer
# from rest_auth.serializers import LoginSerializer
# from rest_auth.models import TokenModel
# from taggit_serializer.serializers import TagListSerializerField, \
#     TaggitSerializer

# from django.contrib.auth import authenticate
# from django.utils.translation import ugettext_lazy as _
# from django.urls import reverse_lazy

# from tags.serializer_fields import NestedTagListSerializerField
from utils.drf.custom_fields import Base64ImageField
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from cases.models import Case
from cases.serializers import CaseCardSerializer
from users.doctors.models import DoctorProfile
from users.doctors.serializers import DoctorDetailSerializer
from .models import ClinicProfile


# pylint: disable=too-few-public-methods
# pylint: disable=missing-docstring


class ClinicPublicSerializer(serializers.HyperlinkedModelSerializer):
    """
    Read only Serializer for showing Clinic information.
    Most of the information are from ClinicProfile.

    """
    uuid = serializers.ReadOnlyField()
    logo_thumbnail = Base64ImageField()
    # concise_regions = serializers.SerializerMethodField()
    # services = NestedTagListSerializerField(source='clinic_profile.services')

    # opening_info = serializers.SerializerMethodField() # tmp
    # rating = serializers.SerializerMethodField()

    # nested field
    branches = serializers.SerializerMethodField()
    services_raw = serializers.ListField() # TODO: use this to make list

    saved_by_user = serializers.SerializerMethodField(required=False)

    # read_only = True
    # source = 'clinic_profile.branches',
    # case_num = serializers.SerializerMethodField()

    def get_branches(self, obj):
        """
        To serialize ArrayModelField from djongo.
        :param obj:
        :return:
        """
        if type(obj.branches) == list:
            embedded_list = []
            for item in obj.branches:
                embedded_dict = item.__dict__
                for key in list(embedded_dict.keys()):
                    if key.startswith('_'):
                        embedded_dict.pop(key)
                    # TODO: tmp fix. PhoneNumber package has bug and is not JSON serializable
                    # https://github.com/stefanfoulis/django-phonenumber-field/issues/225
                    elif key == 'phone':
                        embedded_dict[key] = str(embedded_dict[key])
                    elif key == 'opening_info':
                        # restore the list structure
                        # reason: Djongo abstract model couldn't use ListField..
                        embedded_dict[key] = [] if not embedded_dict[key] \
                            else ast.literal_eval(embedded_dict[key])

                embedded_list.append(embedded_dict)
            return_data = embedded_list
        else:
            embedded_dict = obj.branches
            for key in list(embedded_dict.keys()):
                if key.startswith('_'):
                    embedded_dict.pop(key)
                # TODO: tmp as above
                elif key == 'phone':
                    embedded_dict[key] = str(embedded_dict[key])

            return_data = embedded_dict
        return return_data

    # TODO: WIP
    def get_saved_by_user(self, obj):
        """
        Return a boolean flag indicating whether the user
        in the request saved the current clinic.

        For unauthorized users, it will always be false.

        :param obj: the comment object
        :return (boolean):
        """
        request = self.context.get('request', None)

        # print("reauest", request)

        # for unlogin user
        if not request or request.user.is_anonymous:
            return False

        # it should only have one obj if it's saved
        action_objs = obj.action_object_actions.filter(actor_object_id=request.user._id, verb='save')
        # for item in action_objs:
        #     print("branch_id", item.data['branch_id'])

        # logger.info("action_objs in serializer %s" % action_objs)

        return False if not action_objs else True

    # def get_concise_regions(self, obj):
    #     """
    #     Truncate the ugly 市/縣 words and
    #     remove duplicates.
    #
    #     :param obj: an User object.
    #     :return (string[]): an array of regions
    #
    #     """
    #     d = {}
    #     concise_regions = []
    #     for branch in obj.clinic_profile.branches.all():
    #         # TODO: rewrite the reg
    #         region = branch.region
    #         # alternative is no region
    #         # TODO: bad
    #         if not region and len(branch.branch_name) == 3:
    #             region = branch.branch_name
    #
    #         # truncate
    #         if region and (region.endswith('市')
    #                        or region.endswith('縣')
    #                        or region.endswith('店')):
    #             region = region[:-1]
    #
    #         # remove duplicate
    #         if region and region not in d:
    #             concise_regions.append(region)
    #             d[region] = ''
    #
    #     return concise_regions

    # def get_opening_info(self, obj):
    #     # TODO: deal with empty case
    #     for branch in obj.clinic_profile.branches.all():
    #         if branch.is_head_quarter:
    #             if branch.opening_info:
    #                 return json.loads(branch.opening_info)
    #     return {}

    # def get_case_num(self, obj):
    #     """
    #     Get the number of cases(i.e., posts) that belonged
    #     to this clinic. (default function name for field case_num)
    #
    #     :param obj: an User object
    #     :return (int): reverse foreignkey objects number
    #     """
    #     return obj.clinic_user_posts.count()

    # def get_rating(self, obj):
    #     """
    #     Since in google MAP API, only a location (i.e., a ClinicBranch)
    #     has a rating. So for a Clinic User, we simply average
    #     the ratings from all its branches.
    #
    #     :param obj: an User object
    #     :return (float): the averaged ratings
    #     """
    #     branch_ratings = [branch.rating for branch in obj.branches.all()
    #                       if branch.rating]
    #     # arithmetic average rounded to 1 decimal point
    #     return 0.0 if not branch_ratings else round(sum(branch_ratings)/len(branch_ratings), 1)

    class Meta:
        model = ClinicProfile
        fields = ('website_url', 'uuid', 'user_id', 'display_name',  'logo_thumbnail', 'services_raw',
                  'branches', 'saved_by_user')


class BranchSerializer(serializers.Serializer):
    branch_name = serializers.CharField(required=False)
    place_id = serializers.ReadOnlyField(required=False)
    is_head_quarter = serializers.BooleanField(required=False)
    opening_info = serializers.CharField(required=False)
    rating = serializers.FloatField(required=False)
    address = serializers.CharField(required=False)
    address_help_text = serializers.CharField(required=False)
    region = serializers.CharField(required=False)
    locality = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)


class ClinicHomeSerializer(serializers.HyperlinkedModelSerializer):
    """
    Read only Serializer for clinic home url.

    """
    uuid = serializers.ReadOnlyField()
    logo_thumbnail = Base64ImageField()  # unsure, kinda large, maybe an URL is better
    branch_info = serializers.SerializerMethodField(required=False)
    saved_by_user = serializers.SerializerMethodField(required=False)
    services = serializers.SerializerMethodField(required=False)
    reviews = serializers.SerializerMethodField(required=False)
    cases = serializers.SerializerMethodField(required=False)

    # is_head_quarter = serializers.SerializerMethodField(required=False)

    class Meta:
        model = ClinicProfile
        fields = ('website_url', 'uuid', 'display_name', 'services', 'branch_info',
                  'saved_by_user', 'reviews', 'cases', 'logo_thumbnail')

    # should we add is_head_quarter ?
    def get_branch_info(self, obj):
        request = self.context.get('request', None)
        branch_id = request.query_params.get('branch_id', '')

        print("===branch_id", branch_id)

        # TODO: should I assume it's HQ?
        if not branch_id:
            return ''

        # find the right branch
        for branch in obj.branches or []:
            if branch.branch_id == branch_id:
                serializer = BranchSerializer(branch)
                # reviews = Review.objects.filter(clinic={'place_id': 'ChIJ004m5WipQjQRmBN9dV20Vj4'})
                # serializer.data['reviews'] = ReviewSerializer(reviews, many=True)
                return serializer.data
                # return {"branch_name": branch.branch_name,
                #         "rating":branch.rating}

        # TODO: assumption: data check is in place
        return ''

    # TODO: tmp for now. need normalization
    def get_services(self, obj):
        tokens = obj.services_raw or []
        # tokens
        return ['雙眼皮', '隆鼻', '削骨'] * 3

    # TODO: move out.
    def get_saved_by_user(self, obj):
        """
        Return a boolean flag indicating whether the user
        in the request saved the current clinic.

        For unauthorized users, it will always be false.

        :param obj: the comment object
        :return (boolean):
        """
        # TODO: WIP
        return False
        # request = self.context.get('request', None)
        #
        # # print("reauest", request)
        #
        # # for unlogin user
        # if not request or request.user.is_anonymous:
        #     return False
        #
        # # it should only have one obj if it's saved
        # action_objs = obj.action_object_actions.filter(actor_object_id=request.user._id, verb='save')
        # # for item in action_objs:
        # #     print("branch_id", item.data['branch_id'])
        #
        # # logger.info("action_objs in serializer %s" % action_objs)
        #
        # return False if not action_objs else True

    def get_reviews(self, obj):
        request = self.context.get('request', None)
        branch_id = request.query_params.get('branch_id', '')

        # TODO: should I assume it's HQ?
        if not branch_id:
            return {}  # TODO: not too good

        # find the right branch
        # TODO: pagination
        for branch in obj.branches or []:
            if branch.branch_id == branch_id:
                reviews = Review.objects.filter(clinic={'place_id': branch.place_id})
                serializer = ReviewSerializer(reviews,
                                              many=True,
                                              context={'request': self.context['request']})
                return {"count": len(reviews), "results": serializer.data}
                # return {"branch_name": branch.branch_name,
                #         "rating":branch.rating}

        # TODO: assumption: data check is in place
        return {}

    def get_cases(self, obj):
        """
        TODO: WIP
        :param obj:
        :return:
        """
        cases = Case.objects.filter(clinic={'uuid': obj.uuid},
                                    state="published").order_by('-interest')
        if not cases:
            return {}
        elif len(cases) > 1:
            chosen_case = cases[randint(0, len(cases)-1)]
        else:
            chosen_case = cases[0]

        serializer = CaseCardSerializer(chosen_case,
                                        many=False,
                                        context={'request': self.context['request']})

        # return an array, in case we need to return multiple cases in the future
        return {"count": len(cases),
                "results": [serializer.data]}


# TODO: WIP
class ClinicDoctorsSerializer(serializers.HyperlinkedModelSerializer):
    """
    Read only Serializer for clinic doctor tab.
    """

    doctors = serializers.SerializerMethodField(required=False)

    # can add map data
    class Meta:
        model = ClinicProfile
        fields = ('uuid', 'doctors')

    def get_doctors(self, obj):
        doctors = DoctorProfile.objects.filter(clinic_uuid=obj.uuid)
        serializer = DoctorDetailSerializer(doctors,
                                            many=True,
                                            context={'request': self.context['request']})
        return {"count": len(doctors),
                "results": serializer.data}


class ClinicEsSerializer(serializers.HyperlinkedModelSerializer):
    """
    Read only Serializer for enriching ES record.

    """
    uuid = serializers.ReadOnlyField()
    logo_thumbnail = Base64ImageField()

    # return a list of branch_id of branches saved by users
    saved_by_user = serializers.SerializerMethodField(required=False)

    # read_only = True
    # source = 'clinic_profile.branches',
    # case_num = serializers.SerializerMethodField()

    def get_saved_by_user(self, obj):
        """
        Return a list of branch ids of branch that are saved
        by the user.

        For unauthorized users, it will always be an empty array.

        :param obj: the comment object
        :return (list of str):
        """
        request = self.context.get('request', None)


        # for unlogin user
        if not request or request.user.is_anonymous:
            return []

        # it should only have one obj if it's saved
        action_objs = obj.action_object_actions.filter(actor_object_id=request.user._id, verb='save')

        branch_ids = []
        for item in action_objs:
            branch_id = item.data.get('branch_id', '')
            if branch_id:
                branch_ids.append(branch_id)

        # logger.info("action_objs in serializer %s" % action_objs)
        # return False if not action_objs else True
        return branch_ids

    class Meta:
        model = ClinicProfile
        fields = ('uuid', 'logo_thumbnail', 'saved_by_user')


# TODO: WIP
class ClinicSavedSerializer(serializers.HyperlinkedModelSerializer):
    """
    Read only Serializer for showing Clinic information.
    Most of the information are from ClinicProfile.

    """

    branch_name = serializers.SerializerMethodField(required=False)

    class Meta:
        model = ClinicProfile
        fields = ('website_url', 'uuid', 'user_id', 'display_name',  'logo_thumbnail')

    def get_branch_name(self, obj):
        return ''

# --- Doctor ---

# class DoctorPublicSerializer(serializers.HyperlinkedModelSerializer):
#     """
#
#     """
#     uuid = serializers.ReadOnlyField()
#     # doctor_profile = DoctorProfileSerializer(many=False,
#     #                                          read_only=False)
#
#     clinic_name = serializers.SlugRelatedField(
#         source='doctor_profile.clinic',
#         many=False,
#         read_only=True,
#         slug_field='username'
#     )
#
#     clinic_uuid = serializers.SlugRelatedField(
#         source='doctor_profile.clinic',
#         many=False,
#         read_only=True,
#         slug_field='uuid'
#     )
#
#     position = serializers.SlugRelatedField(
#         source='doctor_profile',
#         many=False,
#         read_only=True,
#         slug_field='position'
#     )
#
#     english_name = serializers.SlugRelatedField(
#         source='doctor_profile',
#         many=False,
#         read_only=True,
#         slug_field='english_name'
#     )
#
#     nick_name = serializers.SlugRelatedField(
#         source='doctor_profile',
#         many=False,
#         read_only=True,
#         slug_field='nick_name'
#     )
#
#     degrees = serializers.SlugRelatedField(
#         source='doctor_profile',
#         many=False,
#         read_only=True,
#         slug_field='degrees'
#     )
#
#     experience = serializers.SlugRelatedField(
#         source='doctor_profile',
#         many=False,
#         read_only=True,
#         slug_field='experiences'
#     )
#
#     certificates = serializers.SlugRelatedField(
#         source='doctor_profile',
#         many=False,
#         read_only=True,
#         slug_field='certificates'
#     )
#
#     services = TagListSerializerField(source='doctor_profile.services')
#
#     fb_url = serializers.SlugRelatedField(
#         source='doctor_profile',
#         many=False,
#         read_only=True,
#         slug_field='fb_url'
#     )
#
#     blog_url = serializers.SlugRelatedField(
#         source='doctor_profile',
#         many=False,
#         read_only=True,
#         slug_field='blog_url'
#     )
#
#     class Meta:
#         model = User
#         fields = ('uuid', 'username', 'clinic_name',
#                   'clinic_uuid', 'position', 'english_name', 'nick_name',
#                   'degrees', 'experience', 'certificates',
#                   'services', 'fb_url', 'blog_url')

