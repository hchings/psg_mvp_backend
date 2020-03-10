"""
Mixins for Django Rest Framework Views.

"""

from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response


class UpdateConciseResponseMixin(UpdateModelMixin):
    """
    Mixins for shorten the response of the
    defulat UpdateModelMixin.

    """

    def update(self, request, *args, **kwargs):
        """
        Update the instance and return:
        1) Title_img url if the request contains an image update
        2) An empty response in other cases

        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # delete the title_img media if receive flag 'delete_title_img'
        # TODO: check robustness of this
        # if 'delete_title_img' in request.data:
        #     # print("Delete title img~")
        #     instance.title_img.delete()

        # print("request data", request.data)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # print('request data', request.data)
        # print('request data', serializer.data)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        # TODO: WIP
        # TODO: this might need changed
        # TODO: this 3 should be ensured to be called separately
        # if 'title_img' in request.data:
        #     return Response({"title_img": serializer.data['title_img']})
        # elif 'images' in request.data:
        #     return Response({"images": serializer.data['images']})
        # elif 'image_url' in request.data:
        #     # TODO: check this
        #     return Response({"images": serializer.data['images']})
        # elif 'image_list' in request.data:
        #     # TODO: add error loggings?
        #     # get the response stored in the context
        #     return Response({"images": serializer.context.get('image_list_urls', [])})
        # else:
        return Response({})
