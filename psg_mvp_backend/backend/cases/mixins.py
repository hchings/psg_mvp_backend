"""
Mixins for Django Rest Framework Views.

"""

from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response

from collections import namedtuple
from hitcount.utils import get_ip
from hitcount.models import BlacklistIP, BlacklistUserAgent

from django.conf import settings

from .models import Hit


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


class MyHitCountMixin(object):
    """
    Mixin to evaluate a HttpRequest and a HitCount and determine whether or not
    the HitCount should be incremented and the Hit recorded.
    """

    @classmethod
    def hit_count_m(self, request, hitcount):
        """
        Called with a HttpRequest and HitCount object it will return a
        namedtuple:
        UpdateHitCountResponse(hit_counted=Boolean, hit_message='Message').
        `hit_counted` will be True if the hit was counted and False if it was
        not.  `'hit_message` will indicate by what means the Hit was either
        counted or ignored.
        """
        UpdateHitCountResponse = namedtuple(
            'UpdateHitCountResponse', 'hit_counted hit_message')

        # as of Django 1.8.4 empty sessions are not being saved
        # https://code.djangoproject.com/ticket/25489
        if request.session.session_key is None:
            request.session.save()

        user = request.user
        try:
            is_authenticated_user = user.is_authenticated()
        except:
            is_authenticated_user = user.is_authenticated
        session_key = request.session.session_key
        ip = get_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
        hits_per_ip_limit = getattr(settings, 'HITCOUNT_HITS_PER_IP_LIMIT', 0)
        exclude_user_group = getattr(settings, 'HITCOUNT_EXCLUDE_USER_GROUP', None)

        # first, check our request against the IP blacklist
        if BlacklistIP.objects.filter(ip__exact=ip):
            return UpdateHitCountResponse(
                False, 'Not counted: user IP has been blacklisted')

        # second, check our request against the user agent blacklist
        if BlacklistUserAgent.objects.filter(user_agent__exact=user_agent):
            return UpdateHitCountResponse(
                False, 'Not counted: user agent has been blacklisted')

        # third, see if we are excluding a specific user group or not
        if exclude_user_group and is_authenticated_user:
            if user.groups.filter(name__in=exclude_user_group):
                return UpdateHitCountResponse(
                    False, 'Not counted: user excluded by group')

        # eliminated first three possible exclusions, now on to checking our database of
        # active hits to see if we should count another one

        # start with a fresh active query set (HITCOUNT_KEEP_HIT_ACTIVE)
        qs = Hit.objects.filter_active()

        # check limit on hits from a unique ip address (HITCOUNT_HITS_PER_IP_LIMIT)
        if hits_per_ip_limit:
            if qs.filter(ip__exact=ip).count() >= hits_per_ip_limit:
                return UpdateHitCountResponse(
                    False, 'Not counted: hits per IP address limit reached')

        # create a generic Hit object with request data
        hit = Hit(session=session_key, hitcount=hitcount.pk, ip=get_ip(request),
                  user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],)

        # print(".....hit", hit)

        # first, use a user's authentication to see if they made an earlier hit
        if is_authenticated_user:
            if not qs.filter(user=str(user.uuid), hitcount=hitcount.pk):
                hit.user = str(user.uuid)  # associate this hit with a user
                hit.save()
                # print("---hit counted, auth user", user.username)
                response = UpdateHitCountResponse(
                    True, 'Hit counted: user authentication')
            else:
                response = UpdateHitCountResponse(
                    False, 'Not counted: authenticated user has active hit')

        # if not authenticated, see if we have a repeat session
        else:
            if not qs.filter(session=session_key, hitcount=hitcount.pk):
                hit.save()
                # print("---hit counted, session", session_key)
                response = UpdateHitCountResponse(
                    True, 'Hit counted: session key')
            else:
                response = UpdateHitCountResponse(
                    False, 'Not counted: session key has active hit')

        return response
