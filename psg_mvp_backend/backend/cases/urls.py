"""
Urls for cases.

"""

# from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views import CaseDetailView, CaseList, CaseSearchView, \
    CaseManageListView, CaseActionList, like_unlike_case

urlpatterns = [
    url(r'^$', CaseList.as_view(), name=CaseList.name),
    url(r'^(?P<uuid>[0-9]+)$', CaseDetailView.as_view(), name=CaseDetailView.name),
    url(r'^search/$', CaseSearchView.as_view(), name=CaseSearchView.name),  # query is in request body
    url(r'^manage-cases/$', CaseManageListView.as_view(), name=CaseManageListView.name),
    url(r'^like/(?P<case_uuid>[^/]+)/?$', like_unlike_case, name='like-case'),
    # TODO: add back flags reg: (?:(?P<flag>[^/]+)/)
    url(r'^unlike/(?P<case_uuid>[^/]+)/?$',
        like_unlike_case,
        {'do_like': False},
        name='unlike-case'),
    url(r'^save/(?P<case_uuid>[^/]+)/?$', like_unlike_case, {'save_unsave': True}, name='like-case'),
    url(r'^unsave/(?P<case_uuid>[^/]+)/?$',
        like_unlike_case,
        {'do_like': False,
         'save_unsave': True},
        name='unlike-case'),
    url(r'^saved/$', CaseActionList.as_view(), name=CaseActionList.name),
]
