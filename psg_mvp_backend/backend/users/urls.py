"""
Urls for Users app.

"""

from rest_auth.registration.views import RegisterView, VerifyEmailView
# from rest_auth.views import PasswordChangeView
from rest_auth.urls import urlpatterns as rest_auth_urls

# from django.contrib.auth.decorators import login_required
from django.conf.urls import url, include
from django.views.generic import TemplateView

from .views import RegisterViewEx, LoginViewEx, verify_username_view, UserInfoView, FacebookLogin, MyPasswordChangeView

# UserList, UserDetail

urlpatterns = [
    # exclude default user and login APIs from django-rest-auth package
    url(r'^login/$', LoginViewEx.as_view(), name=LoginViewEx.name),
    url(r'^', include([url for url in rest_auth_urls
                       if url.name != 'rest_user_details'
                       and url.name != 'rest_login'])),
    url(r'^', include('django.contrib.auth.urls')),  # TODO: tmp, need this for reset email
    url(r'^registration/$', RegisterViewEx.as_view(), name=RegisterViewEx.name),
    url(r'^registration/verify-email/$', VerifyEmailView.as_view(), name='rest_verify_email'),
    url(r'^registration/account-confirm-email/(?P<key>[-:\w]+)/$', TemplateView.as_view(),
        name='account_confirm_email'),
    url(r'^registration/verify-username/$', verify_username_view, name='verity_username'),
    url(r'^password/change/$', MyPasswordChangeView.as_view(), name='rest_password_change'),
    url(r'^user-info/$', UserInfoView.as_view(), name=UserInfoView.name),
    url(r'^facebook/$', FacebookLogin.as_view(), name='fb_login')
    # url(r'^users/$', UserList.as_view(), name=UserList.name),
    # url(r'^users/(?P<pk>[0-9]+)$', UserDetail.as_view(), name=UserDetail.name),
]
