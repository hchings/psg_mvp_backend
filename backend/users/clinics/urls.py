"""
Urls for clinics / doctors.

"""

# from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views import ClinicPublicList, ClinicPublicDetail


urlpatterns = [
    url(r'^$', ClinicPublicList.as_view(), name=ClinicPublicList.name),
    url(r'^(?P<uuid>[0-9]+)$', ClinicPublicDetail.as_view(), name=ClinicPublicDetail.name),
]
