"""
DRF Serializers for reviews.

"""
import coloredlogs, logging
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from django.contrib.auth import get_user_model
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
    pagination_class = PageNumberPagination
    pagination_class.page_size = PAGE_SIZE
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # clinic uuid
        clinic_uuid = str(self.request.query_params.get('clinic_id', ''))
        service = self.request.query_params.get('service', '')
        topic = self.request.query_params.get('topic', '')
        queryset = Review.objects.all()

        if clinic_uuid:
            if service:
                # filter by service
                queryset = queryset.filter(clinic={'uuid': clinic_uuid}, state="published", services=[service])
            else:
                queryset = queryset.filter(clinic={'uuid': clinic_uuid}, state="published")

            if topic:
                queryset = queryset.filter(topics={'topic': topic})

            queryset = queryset.order_by('-created', '-scp_time')

            return queryset

        # most specify clinic uuid
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
