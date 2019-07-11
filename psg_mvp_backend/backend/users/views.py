"""
DRF Views for users and auth.

"""

# from rest_framework import generics, permissions
from rest_auth.registration.views import RegisterView
from rest_auth.views import LoginView
from rest_auth.serializers import LoginSerializer


from django.conf import settings
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterSerializerEx, TokenSerializerEx
    # , \
    # UserSerializer, ClinicPublicSerializer, \
    # DoctorPublicSerializer, TokenSerializerEx
from .models import User
# from .permissions import OnlyAdminCanDelete


# pylint: disable=no-member
# pylint: disable=too-many-ancestors


# --- Auth ---
class RegisterViewEx(RegisterView):
    """
    post: Return a key if successfully registered.

    """
    name = 'rest_register'
    serializer_class = RegisterSerializerEx


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