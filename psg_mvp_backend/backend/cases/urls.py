"""
Urls for cases.

"""

# from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views import CaseDetailView, CaseList, CaseSearchView, \
    CaseManageListView, CaseActionList, like_unlike_case, \
    CaseInviteTokenGenView, CaseInviteInfoDetail, CaseSendInvite, CaseStatsView, \
    CaseUserActionView, CaseSignatureView, ClinicCaseListView

urlpatterns = [
    url(r'^$', CaseList.as_view(), name=CaseList.name),
    url(r'^(?P<uuid>[0-9]+)$', CaseDetailView.as_view(), name=CaseDetailView.name),
    url(r'clinic-cases/(?P<clinic_uuid>[0-9]+)$', ClinicCaseListView.as_view(), name=ClinicCaseListView.name),
    url(r'^search/$', CaseSearchView.as_view(), name=CaseSearchView.name),  # query is in request body
    url(r'^stats/$', CaseStatsView.as_view(), name=CaseStatsView.name),
    url(r'^user-actions/$', CaseUserActionView.as_view(), name=CaseUserActionView.name),
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
    url(r'^invite-gen/$', CaseInviteTokenGenView.as_view(), name=CaseInviteTokenGenView.name),
    url(r'^invite-info/$', CaseInviteInfoDetail.as_view(), name=CaseInviteInfoDetail.name),
    url(r'^send-invite/$', CaseSendInvite.as_view(), name=CaseSendInvite.name),
    url(r'^signatures/$', CaseSignatureView.as_view(), name=CaseSignatureView.name),
]
