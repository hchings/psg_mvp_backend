"""
DRF Views for tags.

"""
from rest_framework.views import APIView
from rest_framework.response import Response

from django.core.cache import cache

from users.clinics.models import ClinicProfile
from backend.shared.utils import _prep_catalog

# store list of surgery mat in memory.
_prep_catalog()



class ClinicNameListView(APIView):
    """
    An un-paginated view that return a list of
    clinic/branch name from ES.

    """
    name = 'clinic-name-list'

    def get(self, request):
        # get from cache if possible
        cache_key = "clinics_names"
        data = cache.get(cache_key)

        # if data:
        #     return Response(data)

        objs = ClinicProfile.objects.filter(is_oob=False).only("display_name")
        res = [{"display_name": obj.display_name} for obj in objs]

        # set cache
        cache.set(cache_key, res)
        return Response(res)


class SurgeryListView(APIView):
    """
    An un-paginated view that return a list of
    catalog with materials from local json.

    """
    name = 'surgery-list'

    def get(self, request):
        """
        
        :param request:
        :return:
        """
        # check cache
        cache_key = 'surgery_tags'
        data = cache.get(cache_key)
        if data:
            return Response(data)

        res, _ = _prep_catalog()
        # set cache
        cache.set(cache_key, res)
        return Response(res)
