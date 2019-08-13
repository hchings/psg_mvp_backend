"""
DRF Serializers for clinics.

"""

import json
import ast

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
from .models import ClinicProfile

# pylint: disable=too-few-public-methods
# pylint: disable=missing-docstring


class ClinicPublicSerializer(serializers.HyperlinkedModelSerializer):
    """
    Read only Serializer for showing Clinic information.
    Most of the information are from ClinicProfile.

    """
    uuid = serializers.ReadOnlyField()
    logo = Base64ImageField()
    # concise_regions = serializers.SerializerMethodField()
    # services = NestedTagListSerializerField(source='clinic_profile.services')

    # opening_info = serializers.SerializerMethodField() # tmp
    # rating = serializers.SerializerMethodField()

    # nested field
    branches = serializers.SerializerMethodField()
    services_raw = serializers.ListField() # TODO: use this to make list

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
        # fields = ('url', 'uuid', 'username', 'logo', 'opening_info',
        #           'concise_regions', 'services', 'rating',
        #           'branches', 'case_num')
        fields = ('website_url', 'uuid', 'user_id', 'display_name', 'logo', 'services_raw',
                  'branches')


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

