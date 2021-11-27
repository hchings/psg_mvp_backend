"""
Urls for doctors.

"""
from django.conf.urls import url

from .views import DoctorPublicList


urlpatterns = [
    url(r'^$', DoctorPublicList.as_view(), name=DoctorPublicList.name),

]
