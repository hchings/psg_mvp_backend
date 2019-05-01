"""
DRF Views for clinics / doctors.

"""

from rest_framework import generics, permissions
# from rest_auth.registration.views import RegisterView
# from rest_auth.views import LoginView

# from django.conf import settings
# from rest_framework.response import Response
# from rest_framework import status

from .serializers import ClinicPublicSerializer
from .models import ClinicProfile
# from .permissions import OnlyAdminCanDelete


# pylint: disable=no-member
# pylint: disable=too-many-ancestors


class ClinicPublicList(generics.ListAPIView):
    """
    get: get a list of info of all the clinics.

    """
    name = 'clinicpublic-list'
    queryset = ClinicProfile.objects.all()
    serializer_class = ClinicPublicSerializer


# TODO: change to list and update only, modify docstring
class ClinicPublicDetail(generics.RetrieveAPIView):
    """
    get: Return the info of a clinic of given uuid.

    """
    name = 'clinicpublic-detail'
    queryset = ClinicProfile.objects.all()
    serializer_class = ClinicPublicSerializer
    lookup_field = 'uuid'
