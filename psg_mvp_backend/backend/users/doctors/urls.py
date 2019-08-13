"""
Urls for doctors.

"""

# from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views import DoctorPublicList


urlpatterns = [
    url(r'^$', DoctorPublicList.as_view(), name=DoctorPublicList.name),
    # url(r'^(?P<uuid>[0-9]+)$', ClinicPublicDetail.as_view(), name=ClinicPublicDetail.name),
    # url(r'^search/(?P<q>\S+)$', ClinicSearchView.as_view(), name=ClinicSearchView.name),  # TODO: can change to ?q=

]
