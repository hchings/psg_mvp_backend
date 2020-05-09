"""
Urls for tags for all features.

"""

from django.conf.urls import url, include


from .views import ClinicNameListView, SurgeryListView

internal_apis = [

]

urlpatterns = [
    url(r'^clinics_names/$', ClinicNameListView.as_view(), name=ClinicNameListView.name),
    url(r'^surgeries/$', SurgeryListView.as_view(), name=SurgeryListView.name),
]
