"""
Urls for comments.

"""

# from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views import CommentListView, CommentDetailView


urlpatterns = [
    url(r'^$', CommentListView.as_view(), name=CommentListView.name),
    url(r'^(?P<uuid>[0-9]+)$', CommentDetailView.as_view(), name=CommentDetailView.name),
]
