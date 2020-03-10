"""
Urls for comments.

"""

# from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views import CommentListView, CommentDetailView, like_unlike_comment

urlpatterns = [
    url(r'^$', CommentListView.as_view(), name=CommentListView.name),
    url(r'^(?P<uuid>[0-9]+)$', CommentDetailView.as_view(), name=CommentDetailView.name),
    url(r'^like/(?P<comment_uuid>[^/]+)/?$', like_unlike_comment, name='like-comment'),
    # TODO: add back flags reg: (?:(?P<flag>[^/]+)/)
    url(r'^unlike/(?P<comment_uuid>[^/]+)/?$',
        like_unlike_comment,
        {'do_like': False},
        name='unlike-comment')
]
