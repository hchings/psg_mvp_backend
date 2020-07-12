"""
DRF Serializers for doctors.

"""

from rest_framework import serializers, exceptions
from annoying.functions import get_object_or_None

from utils.drf.custom_fields import Base64ImageField

from backend.shared.fields import embedded_model_method
from users.clinics.models import ClinicProfile
from .models import DoctorProfile


class DoctorPublicSerializer(serializers.HyperlinkedModelSerializer):
    """
    Read only Serializer for showing brief doctor information.

    """
    uuid = serializers.ReadOnlyField()
    profile_photo = Base64ImageField()

    services_raw = serializers.ListField()  # use this to make list
    clinic_rating = serializers.SerializerMethodField()
    clinic_logo = serializers.SerializerMethodField()
    review_num = serializers.SerializerMethodField()
    case_num = serializers.SerializerMethodField()
    featured_review = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        # TODO: might have better way to use Base64ImageField
        self.img_field = Base64ImageField()
        super().__init__(*args, **kwargs)

    # TODO: how to get clinic_profile obj just once?
    def get_clinic_rating(self, obj):
        clinic_profile_obj = get_object_or_None(ClinicProfile,
                                                uuid=obj.clinic_uuid)
        return '' if not clinic_profile_obj else clinic_profile_obj.rating

    def get_clinic_logo(self, obj):
        clinic_profile_obj = get_object_or_None(ClinicProfile,
                                                uuid=obj.clinic_uuid)

        if not clinic_profile_obj:
            return ''

        return self.img_field.to_representation(clinic_profile_obj.logo_thumbnail)

    def get_review_num(self, obj):
        # TODO: WIP
        return 0
    
    def get_case_num(self, obj):
        # TODO: WIP
        return 0
    
    def get_featured_review(self, obj):
        # TODO: WIP
        return 'this is a feature review.'

    class Meta:
        model = DoctorProfile
        fields = ('uuid', 'display_name', 'profile_photo', 'rating', 'position',
                  'services_raw',  'review_num', 'case_num', 'featured_review', 'is_primary',
                  'clinic_uuid', 'clinic_name', 'clinic_rating', 'clinic_logo')


class DoctorDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
    Read only Serializer for showing detailed doctor information.

    """

    reviews = serializers.SerializerMethodField(required=False)
    cases = serializers.SerializerMethodField(required=False)
    degrees = serializers.SerializerMethodField(required=False)
    certificates = serializers.SerializerMethodField(required=False)
    work_exps = serializers.SerializerMethodField(required=False)

    # TODO: I don't think we'll normalize this
    services_raw = serializers.ListField()  # use this to make list

    class Meta:
        model = DoctorProfile
        fields = ('display_name', 'profile_photo', 'is_primary', 'position',
                  'degrees', 'certificates', 'work_exps',
                  'services_raw', 'youtube_url', 'blog_url', 'fb_url',
                  'reviews', 'cases')

    def get_degrees(self, obj):
        """
        To serialize ArrayModelField from djongo.
        :param obj:
        :return:
        """
        return embedded_model_method(obj,
                                     self.Meta.model,
                                     'degrees',
                                     included_fields=['item'])

    def get_certificates(self, obj):
        """
        To serialize ArrayModelField from djongo.
        :param obj:
        :return:
        """
        return embedded_model_method(obj,
                                     self.Meta.model,
                                     'certificates',
                                     included_fields=['item'])

    def get_work_exps(self, obj):
        """
        To serialize ArrayModelField from djongo.
        :param obj:
        :return:
        """
        return embedded_model_method(obj,
                                     self.Meta.model,
                                     'work_exps',
                                     included_fields=['item'])

    def get_reviews(self, obj):
        # TODO: WIP
        return {}

    def get_cases(self, obj):
        # TODO: WIP
        return {}
