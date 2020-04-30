"""
Urls for tags for all features.

"""

from django.conf.urls import url, include


from .views import ClinicNameListView

internal_apis = [

]

urlpatterns = [
    url(r'^clinics_names/$', ClinicNameListView.as_view(), name=ClinicNameListView.name),
]
