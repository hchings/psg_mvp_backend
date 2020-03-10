"""
DRF Views for clinics.

"""

from collections import OrderedDict

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from elasticsearch_dsl import Q
import coloredlogs, logging
# from hanziconv import HanziConv

# from rest_framework import serializers
# from rest_auth.registration.views import RegisterView
# from rest_auth.views import LoginView

# from django.conf import settings
# from rest_framework.response import Response
# from rest_framework import status

from backend.settings import ES_PAGE_SIZE
from .serializers import ClinicPublicSerializer
from .models import ClinicProfile
# from .permissions import OnlyAdminCanDelete

from utils.drf.custom_fields import Base64ImageField

# from elasticsearch_dsl import connections
# import django_filters.rest_framework
from users.doc_type import ClinicProfileDoc, ClinicBranchDoc

# pylint: disable=no-member
# pylint: disable=too-many-ancestors

# Create a logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class ClinicPublicList(generics.ListAPIView):
    """
    get: get a list of info of all the clinics.

    """
    name = 'clinicpublic-list'
    queryset = ClinicProfile.objects.all()
    serializer_class = ClinicPublicSerializer


# TODO: change to list and update only, modify docstring
class ClinicPublicDetail(generics.RetrieveUpdateAPIView):
    """
    get: Return the info of a clinic of given uuid.

    """
    name = 'clinicpublic-detail'
    queryset = ClinicProfile.objects.all()
    serializer_class = ClinicPublicSerializer
    lookup_field = 'uuid'


class ClinicSearchView(APIView):
    """
    Elasticsearch end point for ClinicProfile
    on branch level.

    ---
    parameters:
        # TODO: add docstring

    """
    name = 'clinicpublic-search'
    # serializer_class = HighScoreSerializer   # don't need this.

    # TODO: should change the serializer to brief serializer
    # TODO: sort tags

    # TODO: API, pagi, other fields
    def post(self, request):
        """
        Return the search result.
        Search query should be specified in request body.
        An example of search query from frontend:

        {
            'keywords': [str1, str2, ...],
            'open_sunday': True
            'clinic_type': str
            'rating_min': 3
        }

        # TODO: add document on response

        :param request:
        :return:
        """
        # since this class does not inherit DRF's generics classes,
        # we need to prepare for the response data ourselves.
        response = OrderedDict({})

        # ----- parse request body -----
        req_body = request.data
        # logger.info("request body for ClinicSearchView %s" % req_body)

        q_combined = None
        if req_body:
            for keyword in req_body.get('keywords', []):
                q_new = Q("multi_match",
                          query=keyword,  # TODO: tmp
                          fields=['display_name', 'services'])
                # logger.info("add keyword %s" % keyword)
                q_combined = q_new if not q_combined else q_combined & q_new  # Q: or | ?

            if 'open_sunday' in req_body:
                # logger.info("add open_sunday")
                q_new = Q({"match": {"open_sunday": req_body['open_sunday']}})
                q_combined = q_new if not q_combined else q_combined & q_new

            if 'rating_min' in req_body:
                # logger.info("add rating_miny")
                q_new = Q({"range": {"rating": {"gte": req_body['rating_min']}}})
                q_combined = q_new if not q_combined else q_combined & q_new

        if not q_combined:
            q_combined = Q({"match_all": {}})

        try:
            # get page num from url para.
            # page number starts from 0.
            page = int(request.query_params.get('page', 0))

            # [IMPORTANT] must set index param when ES has multiple indices.
            # otherwise, it will search on all indices even you set the doc type.
            s = ClinicBranchDoc.search(index='clinic_profile')  # specify search DocType
            s = s.query(q_combined)  # add ES query
            cnt = s.count()  # get number of hits
            total_page = cnt // ES_PAGE_SIZE + 1

            if page >= total_page:
                return Response({'error': 'exceeds page num.'})

            # logger.info("range: %s-%s" % (page*ES_PAGE_SIZE, min((page+1)*ES_PAGE_SIZE, cnt)))
            # Only take minimum number of records that you need for this page from ES by slicing
            res = s[page*ES_PAGE_SIZE: min((page+1)*ES_PAGE_SIZE, cnt)].execute()
            response_dict = res.to_dict()
            hits = response_dict['hits']['hits']

            data, ids = [], []
            data_dict = {}  # for storing an Q(1) mapping from id to source document
            for hit in hits:
                hit['_source']['score'] = hit.get('_score', '')
                doc = hit['_source']
                doc.pop('open_sunday')
                data.append(doc)
                ids.append(hit['_source']['id'])
                data_dict[hit['_source']['id']] = data[-1]

            # get the corresponding objects from mongo.
            # however, Django ORM returns the results in a different order,
            # but it doesn't matter as I only need to get the logos.
            queryset = ClinicProfile.objects.filter(uuid__in=ids)

            # add back info that are not stored in ES engine.
            # since there are only a few fields. It's faster to skip serializer.
            logo_dict = {}
            for clinic in queryset:
                if clinic.uuid not in logo_dict:
                    logo_dict[clinic.uuid] = Base64ImageField().to_representation(clinic.logo_thumbnail)

            # ----- format response ------
            response['count'] = cnt
            response['total_page'] = total_page

            # unlike DRF's pagination where urls of prev/next are returned,
            # for ES we only return page num for simplicity.
            response['prev'] = None if not page else page - 1
            response['next'] = None if page == total_page - 1 else page + 1

            response['results'] = data
            response['logos'] = logo_dict

        except Exception as e:
            # if ES failed. Use django's default way to search obj, which is very slow.
            logger.error("ES Failed on search query %s: %s" % (req_body, e))
            return Response({})
        return Response(response)


# deprecated: clinic-level
# class ClinicSearchView(APIView):
#     """
#     Elasticsearch end point for ClinicProfile.
#     ---
#     parameters:
#       - in: query
#         name: q
#         schema:
#             type: string
#         required: true
#         description: input search query
#
#     """
#     name = 'clinicpublic-search'
#
#     # TODO: more tests on query usage
#     # TODO: should change the serializer to brief serializer
#
#     def get(self, request, q):
#         # query = request.query_params.get('q')
#         query = self.kwargs['q']
#         query = HanziConv.toSimplified(query)
#         ids = []
#         if query:
#             try:
#                 s = ClinicProfileDoc.search()
#                 # format ES query
#                 es_query = Q("multi_match",
#                              query=query,
#                              fields=['display_name', 'obsolete_name', 'english_name'])
#                 s = s.query(es_query)
#                 response = s.execute()
#                 response_dict = response.to_dict()
#                 hits = response_dict['hits']['hits']
#                 ids = [hit['_source']['id'] for hit in hits]
#                 # get the corresponding objects from mongo
#                 queryset = ClinicProfile.objects.filter(_id__in=ids)
#                 clinic_profile_list = list(queryset)
#                 # however, Django ORM returns the results in a different order,
#                 # so we’ll have to reorder them with a sort based on the original ordering of the ids.
#                 clinic_profile_list.sort(key=lambda clinic_profile: ids.index(str(clinic_profile._id)))
#                 serializer = ClinicPublicSerializer(clinic_profile_list, many=True)
#             except Exception as e:
#                 # if ES failed. Use django's default way to search obj, which is very slow.
#                 logger.error("ES Failed on search query %s" % q)
#                 clinic_profiles = ClinicProfile.objects.filter(display_name__icontains=query)
#                 serializer = ClinicPublicSerializer(clinic_profiles, many=True)
#             return Response(serializer.data)
