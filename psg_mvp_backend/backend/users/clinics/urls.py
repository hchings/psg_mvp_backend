"""
Urls for clinics / doctors.

"""

# from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views import ClinicPublicList, ClinicPublicDetail, ClinicSearchView, \
    doctor_name_view, like_unlike_clinic, ClinicSavedList

urlpatterns = [
    url(r'^$', ClinicPublicList.as_view(), name=ClinicPublicList.name),
    url(r'^(?P<uuid>[0-9]+)$', ClinicPublicDetail.as_view(), name=ClinicPublicDetail.name),
    url(r'^doctor_names/(?P<uuid>[0-9]+)$', doctor_name_view, name='doctor_names'),
    url(r'^doctor_names/(?P<clinic_name>\w+)$', doctor_name_view, name='doctor_names'),
    url(r'^search/$', ClinicSearchView.as_view(), name=ClinicSearchView.name),  # query is in request body
    url(r'^save/(?P<clinic_uuid>[^/]+)/?$', like_unlike_clinic, {'save_unsave': True}, name='save-clinic'),
    url(r'^unsave/(?P<clinic_uuid>[^/]+)/?$',
        like_unlike_clinic,
        {'do_like': False,
         'save_unsave': True},
        name='unsave-clinic'),
    url(r'^saved$', ClinicSavedList.as_view(), name=ClinicSavedList.name),
]
