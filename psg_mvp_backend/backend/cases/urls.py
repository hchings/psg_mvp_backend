"""
Urls for cases.

"""

# from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views import CaseDetailView, CaseList, CaseSearchView, CaseManageListView


urlpatterns = [
    url(r'^$', CaseList.as_view(), name=CaseList.name),
    url(r'^(?P<uuid>[0-9]+)$', CaseDetailView.as_view(), name=CaseDetailView.name),
    url(r'^search/$', CaseSearchView.as_view(), name=CaseSearchView.name),  # query is in request body
    url(r'^manage-cases/$', CaseManageListView.as_view(), name=CaseManageListView.name)
]
