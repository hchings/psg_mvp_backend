"""
DRF Serializers for comments.

"""

from annoying.functions import get_object_or_None
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from cases.models import Case
from .models import Comment
from .serializers import CommentSerializer


user_model = get_user_model()


class CommentListView(generics.ListCreateAPIView):
    """
    get: Return a list of comments under the given post id.
    post: Create a new comment.

    """
    name = 'comment-list'
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        """
        Customize Post Response for newly created comment.

        """
        serializer = self.get_serializer(data=request.data)

        err_msg = []
        case_uuid = request.data.get('case_id', '')
        author_uuid = request.data.get('author', {}).get('uuid', '')

        # checker: case uuid and author uuid must be int
        try:
            # print("case uuid", case_uuid, author_uuid)
            # check post id
            if case_uuid:
                _ = int(case_uuid)
                case_obj = get_object_or_None(Case, uuid=case_uuid)
                if not case_obj:
                    err_msg.append('case %s does not exist' % case_uuid)

            if author_uuid:
                _ = int(author_uuid)
                user_obj = get_object_or_None(user_model, uuid=author_uuid)
                if not user_obj:
                    err_msg.append('user %s does not exist' % author_uuid)
        except ValueError as e:
            err_msg.append('uuid must be number string.')

        if err_msg:
            return Response({'error': err_msg},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response({},
                        status=status.HTTP_201_CREATED,
                        headers=headers)


# TODO: WIP
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Return a given comment.
    delete: Delete a given comment.
    patch: Partially update a given comment.
    put: Entirely update a given comment.

    """

    name = 'comment-detail'
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
