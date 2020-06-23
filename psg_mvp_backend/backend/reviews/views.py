"""
DRF Serializers for reviews.

"""

import coloredlogs, logging
# from annoying.functions import get_object_or_None
# from rest_framework.decorators import api_view
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from django.contrib.auth import get_user_model
# from cases.models import Case
# from users.clinics.models import ClinicProfile
# from actstream import actions, action
from .models import Review
from .serializers import ReviewSerializer

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

user_model = get_user_model()
PAGE_SIZE = 10


class ReviewListView(generics.ListCreateAPIView):
    """
    get: Return a list of comments under the given clinic uuid.
    post: Create a new review.

    """
    name = 'review-list'
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # this will give "http://localhost:8000/comments/?case_id=1656029043902246&page=2"
    pagination_class = PageNumberPagination
    pagination_class.page_size = PAGE_SIZE
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # clinic uuid
        clinic_uuid = str(self.request.query_params.get('clinic_id', ''))
        queryset = Review.objects.all()

        if clinic_uuid:
            queryset = queryset.filter(clinic={'uuid': clinic_uuid})
            return queryset

        # TODO: most specify clinic uuid
        return []

    def create(self, request, *args, **kwargs):
        """
        Customize Post Response for newly created review.

        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response({"id": str(serializer.data['uuid'])},
                        status=status.HTTP_201_CREATED,
                        headers=headers)


# TODO: WIP. maybe remove update view?
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Return a given comment.
    delete: Delete a given comment.
    patch: Partially update a given comment.
    put: Entirely update a given comment.

    """

    name = 'review-detail'
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticatedOrReadOnly]

    # not working
    # def get_serializer_context(self):
    #     return {'request': self.request}


# act stream TODO: WIP
# @api_view(['POST'])
# def like_unlike_comment(request, comment_uuid, flag='', do_like=True, actor_only=False):
#     """
#     DRF Funcional-based view to like or unlike a user.
#     Note that for each comment, we'll at most have 2 activity stream objects (like and unlike).
#     Making a like API call when like is already the latest object will do no action.
#     Making an unlike API call in the same situation will wipe out the previous unlike records
#     and stack a new one.
#
#
#     :param request: RESTful request.
#     :param comment_uuid: the target to be followed. (The model is Comment.)
#     :param flag: -
#     :param do_like: a flag so that both the follow and unfollow urls can
#                       share this same view.
#     :param actor_only: -
#     :return:
#     """
#     # print("like unlike comment", comment_uuid)
#
#     if not request.user.is_authenticated:
#         logger.error('Unauthenticated user using like/unlike API.')
#         # TODO: find default msg, think how to handle at client is more convenient
#         return Response({'error': 'unauthenticated user'}, status.HTTP_401_UNAUTHORIZED)
#
#     # get target instance
#     # instance = get_object_or_404(get_user_model(), username=object_username)
#
#     # get action object
#     comment_obj = get_object_or_None(Comment, uuid=comment_uuid)
#
#     if not comment_uuid:
#         return Response({'error': 'invalid comment id'}, status.HTTP_400_BAD_REQUEST)
#
#     verb = 'like' if do_like else 'unlike'
#
#     res = comment_obj.action_object_actions.filter(actor_object_id=request.user._id).order_by('-timestamp')
#
#     # print("res of ac stream", res, verb)
#
#     if res and res[0].verb == verb:
#         return Response({'succeed': 'duplicated %s action is ignored.' % verb}, status.HTTP_201_CREATED)
#
#     # else
#     if len(res) >= 2:
#         # negative index not supported
#         res[len(res)-1].delete()
#
#     action.send(request.user, verb=verb, action_object=comment_obj)
#     return Response({'succeed': ""}, status.HTTP_201_CREATED)
#
#     # if do_like:
#     #     # TODO: diff btwn actions and action??
#     #     # note that this built-in follow function
#     #     # will automatically generate an action
#     #
#     #     # check like
#     #     # actor_object_id is the mongo document id
#     #     res = comment_obj.action_object_actions.filter(verb='like', actor_object_id=request.user._id)
#     #     if res:
#     #         return Response({'succeed': 'duplicated action is ignored.'}, status.HTTP_204_NO_CONTENT)
#     #
#     #     action.send(request.user, verb='like', action_object=comment_obj) # TODO: WIP
#     #     # action.send(request.user, verb='created comment', action_object=comment, target=group)
#     #
#     #     # actions.follow(request.user,
#     #     #                instance,
#     #     #                actor_only=actor_only,
#     #     #                flag=flag)
#     #     # TODO: a try on django-notification
#     #     # notify.send(request.user, recipient=instance, verb='is following you.')
#     #
#     #     # publish notification msg through websocket if the target user
#     #     # is online
#     #
#     #     # TODO: WIP: change to async
#     #     # channel_layer = get_channel_layer()
#     #     # group_name = 'notif_%s' % instance.uuid
#     #
#     #     # await channel_layer.group_send(
#     #     #     chat_name,
#     #     #     {"type": "chat.system_message", "text": announcement_text},
#     #     # )
#     #
#     #     # print("Get channel layer", channel_layer, group_name)
#     #     # async_to_sync(channel_layer.group_send)(group_name,
#     #     #                                         {"type": "followed_by_notif",
#     #     #                                          "actor": request.user.username})
#     #     # TODO: WIP
#     #     return Response({"succeed": ""},
#     #                     status=status.HTTP_201_CREATED)
#     #
#     # else:
#     #     # check unlike
#     #     # actor_object_id is the mongo document id
#     #     res = comment_obj.action_object_actions.filter(verb='unlike', actor_object_id=request.user._id)
#     #     if res:
#     #         return Response({'succeed': 'duplicated action is ignored.'}, status.HTTP_204_NO_CONTENT)
#     #
#     #     action.send(request.user, verb='unlike', action_object=comment_obj)
#     #     return Response({'succeed': ""}, status.HTTP_204_NO_CONTENT)



# ReviewListView, ReviewDetailView, like_unlike_review
