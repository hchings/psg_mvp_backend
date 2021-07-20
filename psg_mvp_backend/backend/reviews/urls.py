"""
Urls for reviews.

"""

# from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views import ReviewListView, ReviewDetailView\
    # , like_unlike_review

urlpatterns = [
    url(r'^$', ReviewListView.as_view(), name=ReviewListView.name),
    url(r'^(?P<uuid>[0-9]+)$', ReviewDetailView.as_view(), name=ReviewDetailView.name),
    # url(r'^like/(?P<review_uuid>[^/]+)/?$', like_unlike_review, name='like-review'),
    # url(r'^unlike/(?P<review_uuid>[^/]+)/?$',
    #     like_unlike_review,
    #     {'do_like': False},
    #     name='unlike-comment')
]
