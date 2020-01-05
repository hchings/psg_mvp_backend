"""
DRF Views for tags.

"""

from rest_framework.views import APIView
from rest_framework.response import Response
from elasticsearch_dsl import Q

from users.doc_type import ClinicBranchDoc


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
        s = ClinicBranchDoc.search()
        s = s.query(q).source(["display_name", "branch_name"])
        cnt = s.count()

        res = s[0:cnt].execute()  # you cannot print this

        response_dict = res.to_dict()
        hits = response_dict['hits']['hits']

        res = [item['_source'] for item in hits]
        # print(response_dict)

        return Response(res)
