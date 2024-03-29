"""
Urls for clinics / doctors.

"""
from django.conf.urls import url

from .views import ClinicPublicList, ClinicPublicDetail, \
    doctor_name_view, like_unlike_clinic, ClinicSavedList, ClinicHome, \
    ClinicDoctors, ClinicPricePointsList, clinic_id_view

urlpatterns = [
    url(r'^$', ClinicPublicList.as_view(), name=ClinicPublicList.name),
    url(r'^(?P<uuid>[0-9]+)$', ClinicPublicDetail.as_view(), name=ClinicPublicDetail.name),  # internal use only
    url(r'^home/(?P<uuid>[0-9]+)$', ClinicHome.as_view(), name=ClinicHome.name),  # TODO: WIP. take in ?branch_id=<>
    url(r'^doctors/(?P<uuid>[0-9]+)$', ClinicDoctors.as_view(), name=ClinicDoctors.name),  # TODO: WIP
    url(r'^doctor_names/(?P<uuid>[0-9]+)$', doctor_name_view, name='doctor_names'),
    url(r'^doctor_names/(?P<clinic_name>\w+)$', doctor_name_view, name='doctor_names'),
    url(r'^save/(?P<clinic_uuid>[^/]+)/?$', like_unlike_clinic, {'save_unsave': True}, name='save-clinic'),
    url(r'^unsave/(?P<clinic_uuid>[^/]+)/?$',
        like_unlike_clinic,
        {'do_like': False,
         'save_unsave': True},
        name='unsave-clinic'),
    url(r'^saved$', ClinicSavedList.as_view(), name=ClinicSavedList.name),
    url(r'^price_points/(?P<uuid>[0-9]+)$', ClinicPricePointsList.as_view(), name=ClinicPricePointsList.name),
    url(r'^id/(?P<clinic_name>.+)$', clinic_id_view, name='clinic_id'),
]
