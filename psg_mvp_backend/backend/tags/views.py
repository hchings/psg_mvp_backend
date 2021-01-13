"""
DRF Views for tags.

"""
from rest_framework.views import APIView
from rest_framework.response import Response
from elasticsearch_dsl import Q
from elasticsearch.exceptions import NotFoundError

from django.core.cache import cache
from django.core.management import call_command

from users.doc_type import ClinicBranchDoc
from backend.shared.utils import _prep_catalog

# store list of surgery mat in memory.
_prep_catalog()

# no need pagination as it's for auto-complete
# leverage the branch level data in ES


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

        if data:
            return Response(data)

        q = Q({"match_all": {}})
        # [IMPORTANT] must set index param when ES has multiple indices.
        # otherwise, it will search on all indices even you set the doc type.
        s = ClinicBranchDoc.search(index='clinic_profile')
        s = s.query(q).source(["display_name", "branch_name"])

        try:
            cnt = s.count()
        except NotFoundError as e:
            print("Error in clinic-name-list: %s, reload index" % str(e))
            call_command('index_clinic_profiles')
            cnt = s.count()

        res = s[0:cnt].execute()  # you cannot print this

        response_dict = res.to_dict()
        hits = response_dict['hits']['hits']

        res = [item['_source'] for item in hits]
        # print(response_dict)

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
