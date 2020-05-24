"""
DRF Views for tags.

"""
import json, os

from rest_framework.views import APIView
from rest_framework.response import Response
from elasticsearch_dsl import Q

from users.doc_type import ClinicBranchDoc
from backend.settings import FIXTURE_ROOT


# note that this is relevant to the top app folder
CATALOG_FILE = os.path.join(FIXTURE_ROOT, 'catalog.json')
surgery_mat_list = []


# no need pagination as it's for auto-complete
# leverage the branch level data in ES


class ClinicNameListView(APIView):
    """
    An un-paginated view that return a list of
    clinic/branch name from ES.

    """
    name = 'clinic-name-list'

    def get(self, request):
        q = Q({"match_all": {}})
        # [IMPORTANT] must set index param when ES has multiple indices.
        # otherwise, it will search on all indices even you set the doc type.
        s = ClinicBranchDoc.search(index='clinic_profile')
        s = s.query(q).source(["display_name", "branch_name"])
        cnt = s.count()

        res = s[0:cnt].execute()  # you cannot print this

        response_dict = res.to_dict()
        hits = response_dict['hits']['hits']

        res = [item['_source'] for item in hits]
        # print(response_dict)

        return Response(res)


class SurgeryListView(APIView):
    """
    An un-paginated view that return a list of
    catalog with materials from local json.

    """
    name = 'surgery-list'

    @staticmethod
    def _prep_catalog():
        """
        Prep for surgery stuff.
        Only read file for once on initial call.
        Values will be cached.

        :return:
        """
        # read in json catalog only once
        if not surgery_mat_list:
            catalog_dict = {}
            with open(CATALOG_FILE) as json_file:
                catalog_dict = json.load(json_file)

            for item in catalog_dict.get('catalog_items', []):
                for subcat in item.get('subcategory', []):
                    name = subcat.get('name', '')
                    if name:
                        # pop key if exist
                        subcat.pop('syn', None)
                        surgery_mat_list.append(subcat)

        return surgery_mat_list

    def get(self, request):
        """
        
        :param request:
        :return:
        """
        res = self._prep_catalog()

        return Response(res)
