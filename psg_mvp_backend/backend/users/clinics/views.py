"""
DRF Views for clinics.

"""

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from elasticsearch_dsl import Q
import coloredlogs, logging
from hanziconv import HanziConv


# from rest_auth.registration.views import RegisterView
# from rest_auth.views import LoginView

# from django.conf import settings
# from rest_framework.response import Response
# from rest_framework import status

from .serializers import ClinicPublicSerializer
from .models import ClinicProfile
# from .permissions import OnlyAdminCanDelete


# from elasticsearch_dsl import connections
# import django_filters.rest_framework
from users.doc_type import ClinicProfileDoc


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


# TODO: sort out what kind of searches we need
# TODO: need to transfer the query into simpilifed chinese first
# Get ids from the result and do query in the real DB.
class ClinicSearchView(APIView):
    """
    Elasticsearch end point for ClinicProfile.
    ---
    parameters:
      - in: query
        name: q
        schema:
            type: string
        required: true
        description: input search query

    """
    name = 'clinicpublic-search'

    # TODO: more tests on query usage
    # TODO: should change the serializer to brief serializer

    def get(self, request, q):
        # query = request.query_params.get('q')
        query = self.kwargs['q']
        query = HanziConv.toSimplified(query)
        ids = []
        if query:
            try:
                s = ClinicProfileDoc.search()
                # format ES query
                es_query = Q("multi_match",
                             query=query,
                             fields=['display_name', 'obsolete_name', 'english_name'])
                s = s.query(es_query)
                response = s.execute()
                response_dict = response.to_dict()
                hits = response_dict['hits']['hits']
                ids = [hit['_source']['id'] for hit in hits]
                # get the corresponding objects from mongo
                queryset = ClinicProfile.objects.filter(_id__in=ids)
                clinic_profile_list = list(queryset)
                # however, Django ORM returns the results in a different order,
                # so we’ll have to reorder them with a sort based on the original ordering of the ids.
                clinic_profile_list.sort(key=lambda clinic_profile: ids.index(str(clinic_profile._id)))
                serializer = ClinicPublicSerializer(clinic_profile_list, many=True)
            except Exception as e:
                # if ES failed. Use django's default way to search obj, which is very slow.
                logger.error("ES Failed on search query %s" % q)
                clinic_profiles = ClinicProfile.objects.filter(display_name__icontains=query)
                serializer = ClinicPublicSerializer(clinic_profiles, many=True)
            return Response(serializer.data)
