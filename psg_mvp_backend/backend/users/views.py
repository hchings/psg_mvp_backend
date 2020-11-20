"""
DRF Views for users and auth.

"""

from hashlib import md5
import coloredlogs, logging
from datetime import timedelta

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView

# import pytz

from django.utils import timezone

# from rest_framework import generics, permissions
from rest_auth.registration.views import RegisterView
from rest_auth.views import LoginView
from rest_auth.serializers import LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from annoying.functions import get_object_or_None

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from backend.shared.utils import random_with_n_digits
from cases.models import Case

from .serializers import RegisterSerializerEx, TokenSerializerEx
from .models import User, RegistrationOTP

# from .permissions import OnlyAdminCanDelete


# pylint: disable=no-member
# pylint: disable=too-many-ancestors

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

# fixed otp length
OTP_LENGTH = 6

# for getting actions
case_content_type = ContentType.objects.get(model='case')


# --- Auth ---
class RegisterViewEx(RegisterView):
    """
    post: Return a key if successfully registered.

    If no OTP payload sent to the endpoint, it will gen code and send through email.
    Otherwise, it will read code and either complete registration or error out.

    """
    name = 'rest_register'
    serializer_class = RegisterSerializerEx

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # 1. validate sign up form (this might throw out already exist or pw too common errors)
        serializer.is_valid(raise_exception=True)

        # 2. parse otp code and get hashed_email
        # print("check data", serializer.data)
        otp_code = serializer.data.get('otp', '')

        try:
            hashed_email = md5(serializer.data.get('email', '').encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error("[ERROR] RegisterViewEx md5: %s " % str(e))
            hashed_email = serializer.data.get('email', '')

        if not otp_code:
            # 3. if no otp code in request, gen an otp code,
            #    no registration action will happen.
            otp_new = random_with_n_digits(OTP_LENGTH)
            # TODO what if email = null?
            otp_obj = RegistrationOTP(hashed_email=hashed_email,
                                      otp=otp_new)
            otp_obj.save()
            # print("otp code", otp_new)

            headers = self.get_success_headers(serializer.data)
            return Response({'success': 'verification email sent.'},
                            status=status.HTTP_201_CREATED,
                            headers=headers)
        else:
            # 4. if got otp code, search for valid token gen within 30 mins.
            #    if found, complete the registration flow.
            #    TODO: haven't tested, WIP
            time_threshold = timezone.now() - timedelta(minutes=30)
            # tokens are valid only if they are created within 30 mins from now.
            otp_res = RegistrationOTP.objects.filter(hashed_email=hashed_email,
                                                     otp=otp_code,
                                                     created__gt=time_threshold)

            # print("opt_res", otp_res)
            if len(otp_res) > 0:
                # print("-----------opt code correct, registered")
                user = self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(self.get_response_data(user),
                                status=status.HTTP_201_CREATED,
                                headers=headers)
            else:
                return Response({'otp': 'invalid code'},
                                status=status.HTTP_400_BAD_REQUEST)


class LoginViewEx(LoginView):
    """
    post: Return key, uuid, and username
    if the credentials are correct.

    """
    name = 'rest_login'
    serializer_class = LoginSerializer

    # TODO: WIP
    def get_response(self):
        """
        Override the same method in rest_auth package
        to customize the login response.
        post() will call this.

        (Only the serializer is modified.)

        :return:
        """
        # use my customized serializer
        serializer_class = TokenSerializerEx

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': self.user,
                'token': self.token
            }
            serializer = serializer_class(instance=data,
                                          context={'request': self.request})
        # goes here for now
        else:
            # token in an obj from rest_auth's TokenModel
            serializer = serializer_class(instance=self.token,
                                          context={'request': self.request})

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def verify_username_view(request):
    """
    A simple view to verity whether a username is too short
    or already exist.

    """
    username = request.query_params.get('username', '').strip()

    if len(username) < 3:
        return Response({'error': "username too short."}, status.HTTP_200_OK)

    user = get_object_or_None(User, username=username, user_type='user')

    if not user:
        return Response({'succeed': "valid username."}, status.HTTP_200_OK)
    else:
        return Response({'error': "username exists."}, status.HTTP_200_OK)


# TODO: WIP
class UserInfoView(generics.RetrieveAPIView):
    name = 'user-info'
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """


        :param request:
        :return:
        """

        # 1. get saved cnt
        user = request.user
        saved_cases = user.actor_actions.filter(action_object_content_type=case_content_type,
                                                verb='save')

        # get the action object
        case_set = set()
        saved_cnt = 0
        for item in saved_cases:
            if item not in case_set:
                saved_cnt += 1

        # 2, 3. get review/published cnt
        review_cnt = Case.objects.filter(author={'uuid': str(user.uuid)},
                            state='reviewing').count()
        published_cnt = Case.objects.filter(author={'uuid': str(user.uuid)},
                                         state='published').count()

        return Response({'saved_cnt': saved_cnt,
                         'review_cnt': review_cnt,
                         'published_cnt': published_cnt}, status.HTTP_200_OK)


# # --- User ---
# class UserList(generics.ListAPIView):
#     """
#     get: Return a list of all the existing users.
#
#     """
#     name = 'user-list'
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     filter_fields = ('user_type', )
#     # TODO: add permissions
#
# class UserDetail(generics.RetrieveUpdateDestroyAPIView):
#     """
#     delete: Delete a user of given id.
#     get: Return a user of given id.
#     patch: Apply partial modification to a user of given id.
#     put: Replace a user of given id with the request payload.
#
#     """
#     name = 'user-detail'
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#     # permission_classes = (OnlyAdminCanDelete,)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
