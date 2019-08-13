"""
DRF Views for doctors.

"""

from rest_framework import generics, permissions
import coloredlogs, logging

from .serializers import DoctorPublicSerializer
from .models import DoctorProfile


# pylint: disable=no-member
# pylint: disable=too-many-ancestors

# Create a logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class DoctorPublicList(generics.ListAPIView):
    """
    get: get a list of info of all the doctors.

    """
    name = 'doctorpublic-list'
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorPublicSerializer
