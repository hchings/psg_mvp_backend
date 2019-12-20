"""
Urls for clinics / doctors.

"""

# from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views import ClinicPublicList, ClinicPublicDetail, ClinicSearchView


urlpatterns = [
    url(r'^$', ClinicPublicList.as_view(), name=ClinicPublicList.name),
    url(r'^(?P<uuid>[0-9]+)$', ClinicPublicDetail.as_view(), name=ClinicPublicDetail.name),
    url(r'^search/$', ClinicSearchView.as_view(), name=ClinicSearchView.name),  # query is in request body
]
