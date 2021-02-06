"""
DRF Serializers for Users app.

"""

from rest_framework import serializers, exceptions
from rest_auth.registration.serializers import RegisterSerializer
# from rest_auth.serializers import LoginSerializer
from rest_auth.models import TokenModel
from rest_auth.serializers import PasswordResetSerializer

# from taggit_serializer.serializers import TagListSerializerField, \
#     TaggitSerializer

# from django.contrib.auth import authenticate
# from django.utils.translation import ugettext_lazy as _
# from django.urls import reverse_lazy

# from tags.serializer_fields import NestedTagListSerializerField

# from backend.shared.drf.custom_fields import Base64ImageField
from .models import User
# from .tasks import send_forget_pw_reset

# from .profile_models import ClinicBranch

# pylint: disable=too-few-public-methods
# pylint: disable=missing-docstring

USER_TYPES = [choice_tuple[0] for choice_tuple in User.USER_TYPE_CHOICES]


class RegisterSerializerEx(RegisterSerializer):
    """
    Registration Serializer extended from RegisterSerializer
    in django-rest-auth package.

    """
    user_type = serializers.ChoiceField(USER_TYPES, default='user')
    otp = serializers.CharField(required=False, allow_blank=True)

    def save(self, request):
        """
        Override parent method to save extra fields
        in User model during registration.

        :return (User): a newly created user object.

        """
        user = super().save(request)
        user_type = self.validated_data.get('user_type', 'user')
        user.user_type = user_type
        user.save()

        return user


# TODO: WIP
class TokenSerializerEx(serializers.ModelSerializer):
    """
    Extension serializer for token.
    Used to customize the login response.

    """
    uuid = serializers.SlugRelatedField(source='user',
                                        many=False,
                                        read_only=True,
                                        slug_field='uuid')
    username = serializers.SlugRelatedField(source='user',
                                            many=False,
                                            read_only=True,
                                            slug_field='username')

    # is staff
    stf = serializers.SlugRelatedField(source='user',
                                       many=False,
                                       read_only=True,
                                       slug_field='is_staff')

    class Meta:
        model = TokenModel
        fields = ('key', 'uuid', 'username', 'stf')


# reset password
class CustomPasswordResetSerializer(PasswordResetSerializer):
    """
    Customize django-rest-auth email. See stackoverflow.
    """
    def get_email_options(self):
        return {
            'subject_template_name': 'registration/custom_password_reset_subject.txt',
            'email_template_name': 'registration/custom_password_reset_email.html',
            'domain_override': 'surgi.fyi'
            # 'html_email_template_name': 'registration/'
            #                             'password_reset_message.html',
            # 'extra_email_context': {
            #     'pass_reset_obj': self.your_extra_reset_obj
        }

# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     """
#     Serializer for User model.
#
#     """
#     # profile = serializers.HyperlinkedRelatedField(many=False,
#     #                                               view_name='userprofile-detail',
#     #                                               read_only=True)
#
#     # reverse relationship to Review Model (One-to-Many)
#     # reviews = serializers.HyperlinkedRelatedField(many=True,
#     #                                               read_only=True,
#     #                                               view_name='review-detail')
#
#     class Meta:
#         model = User
#         fields = ('url', 'id', 'username', 'email', 'user_type')
