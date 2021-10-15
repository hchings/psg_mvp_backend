"""
DRF Views for clinics.

"""
from urllib.parse import urlparse
from collections import OrderedDict

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from elasticsearch_dsl import Q
import coloredlogs, logging
from annoying.functions import get_object_or_None
from actstream import actions, action
# from actstream.models import Action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from django.contrib.contenttypes.models import ContentType

from backend.settings import ES_PAGE_SIZE
from backend.shared.permissions import IsAdminOrReadOnly, IsAdminOrIsClinicOwner
from .serializers import ClinicPublicSerializer, ClinicSavedSerializer, \
    ClinicEsSerializer, ClinicHomeSerializer, ClinicDoctorsSerializer
from .models import ClinicProfile
# from .permissions import OnlyAdminCanDelete

from utils.drf.custom_fields import Base64ImageField

# from elasticsearch_dsl import connections
# import django_filters.rest_framework
from users.doc_type import ClinicProfileDoc, ClinicBranchDoc
from users.doctors.models import DoctorProfile

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
    permission_classes = [IsAdminOrIsClinicOwner]


# class ClinicSearchView(APIView):
#     """
#     Elasticsearch end point for ClinicProfile
#     on branch level.
#
#     ---
#     parameters:
#         # TODO: add docstring
#
#     """
#     name = 'clinicpublic-search'
#
#     # serializer_class = HighScoreSerializer   # don't need this.
#
#     # TODO: should change the serializer to brief serializer
#     # TODO: sort tags
#
#     # TODO: API, pagi, other fields
#     def post(self, request):
#         """
#         Return the search result.
#         Search query should be specified in request body.
#         An example of search query from frontend:
#
#         {
#             'keywords': [str1, str2, ...],
#             # 'open_sunday': True
#             'clinic_type': str
#             'rating_min': 3
#         }
#
#         # TODO: add document on response
#
#         :param request:
#         :return:
#         """
#         # since this class does not inherit DRF's generics classes,
#         # we need to prepare for the response data ourselves.
#         response = OrderedDict({})
#
#         # ----- parse request body -----
#         req_body = request.data
#         logger.info("request body for ClinicSearchView ori %s" % req_body)
#
#         q_combined = None
#         if req_body:
#             for keyword in req_body.get('keywords', []):
#                 q_new = Q("multi_match",
#                           query=keyword,  # TODO: tmp
#                           fields=['display_name', 'services'])
#                 # logger.info("add keyword %s" % keyword)
#                 q_combined = q_new if not q_combined else q_combined & q_new  # Q: or | ?
#
#             # TODO: should change to filter query
#             if 'open_sunday' in req_body:
#                 # logger.info("add open_sunday")
#                 q_new = Q({"match": {"open_sunday": req_body['open_sunday']}})
#                 q_combined = q_new if not q_combined else q_combined & q_new
#
#             if 'rating_min' in req_body:
#                 # logger.info("add rating_miny")
#                 q_new = Q({"range": {"rating": {"gte": req_body['rating_min']}}})
#                 q_combined = q_new if not q_combined else q_combined & q_new
#
#         if not q_combined:
#             q_combined = Q({"match_all": {}})
#
#         try:
#             # get page num from url para.
#             # page number starts from 0.
#             page = int(request.query_params.get('page', 0))
#
#             # [IMPORTANT] must set index param when ES has multiple indices.
#             # otherwise, it will search on all indices even you set the doc type.
#             s = ClinicBranchDoc.search(index='clinic_profile')  # specify search DocType
#             s = s.query(q_combined)  # add ES query
#             cnt = s.count()  # get number of hits
#             total_page = cnt // ES_PAGE_SIZE + 1
#
#             if page >= total_page:
#                 return Response({'error': 'exceeds page num.'})
#
#             # logger.info("range: %s-%s" % (page*ES_PAGE_SIZE, min((page+1)*ES_PAGE_SIZE, cnt)))
#             # Only take minimum number of records that you need for this page from ES by slicing
#             res = s[page * ES_PAGE_SIZE: min((page + 1) * ES_PAGE_SIZE, cnt)].execute()
#             response_dict = res.to_dict()
#             hits = response_dict['hits']['hits']
#
#             print("========hits", hits)
#
#             data, ids = [], set()
#             data_dict = {}  # for storing an Q(1) mapping from branch id to source document
#             for hit in hits:
#                 hit['_source']['score'] = hit.get('_score', '')
#                 doc = hit['_source']
#                 doc.pop('open_sunday')
#                 doc['saved_by_user'] = False  # pre-fill
#                 data.append(doc)
#                 ids.add(hit['_source']['id'])
#                 data_dict['_'.join([hit['_source']['id'],
#                                     hit['_source']['branch_id']])] = data[-1]
#
#             # get the corresponding objects from mongo.
#             # however, Django ORM returns the results in a different order,
#             # but it doesn't matter as I only need to get the logos.
#             queryset = ClinicProfile.objects.filter(uuid__in=ids)
#             serializer = ClinicEsSerializer(list(queryset),
#                                             many=True,
#                                             context={'request': request})
#
#             # add back info that are not stored in ES engine. (e.g., 'saved_by_user')
#             logo_dict = {}
#
#             for clinic in serializer.data:
#                 clinic_uuid = clinic['uuid']
#                 # print("clinic %s, %s" % (clinic['uuid'], clinic['saved_by_user']))
#                 for branch_id in clinic['saved_by_user']:
#                     identifier = '_'.join([clinic_uuid, branch_id])
#                     if identifier in data_dict:
#                         data_dict[identifier]['saved_by_user'] = True
#                 if clinic_uuid not in logo_dict:
#                     logo_dict[clinic_uuid] = clinic['logo_thumbnail']  # TODO: base64?
#
#             # ----- format response ------
#             response['count'] = cnt
#             response['total_page'] = total_page
#
#             # unlike DRF's pagination where urls of prev/next are returned,
#             # for ES we only return page num for simplicity.
#             response['prev'] = None if not page else page - 1
#             response['next'] = None if page == total_page - 1 else page + 1
#
#             response['results'] = data
#             response['logos'] = logo_dict
#
#         except Exception as e:
#             # if ES failed. Use django's default way to search obj, which is very slow.
#             logger.error("ES Failed on search query %s: %s" % (req_body, e))
#             return Response({})
#         return Response(response)


class ClinicSearchView(APIView):
    """
    Elasticsearch end point for ClinicProfile
    on branch level.

    ---
    parameters:
        # TODO: add docstring

    """
    name = 'clinicpublic-search'

    def post(self, request):
        """
        Return the search result.
        Search query should be specified in request body.
        An example of search query from frontend:

        {
            'keywords': [str1, str2, ...],
            'clinic_type': str
            'rating_min': 3
            'region':"#%@"
            'sorting':'num_cases|num_reviews'
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
        logger.info("request body for ClinicSearchView %s" % req_body)

        q_combined = None
        if req_body:
            for keyword in req_body.get('keywords', []):
                q_new = Q("multi_match",
                          query=keyword,  # TODO: tmp
                          fields=['display_name', 'services'])
                # logger.info("add keyword %s" % keyword)
                q_combined = q_new if not q_combined else q_combined & q_new  # Q: or | ?

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
            s = ClinicProfileDoc.search(index='clinic_profile')  # specify search DocType
            s = s.query(q_combined)  # add ES query
            if "region" in req_body:
                s = s.filter('term', regions=req_body['region'])

            sorting_method = req_body.get('sorting', '')
            if sorting_method == 'num_cases':
                s = s.sort('-num_cases')
            elif sorting_method == "num_reviews":
                s = s.sort('-num_reviews')

            cnt = s.count()  # get number of hits
            total_page = cnt // ES_PAGE_SIZE + 1

            if page >= total_page:
                return Response({'error': 'exceeds page num.'})

            # logger.info("range: %s-%s" % (page*ES_PAGE_SIZE, min((page+1)*ES_PAGE_SIZE, cnt)))
            # Only take minimum number of records that you need for this page from ES by slicing
            res = s[page * ES_PAGE_SIZE: min((page + 1) * ES_PAGE_SIZE, cnt)].execute()
            response_dict = res.to_dict()
            hits = response_dict['hits']['hits']

            data, ids = [], set()
            url = urlparse(request.build_absolute_uri())
            for hit in hits:
                hit['_source']['score'] = hit.get('_score', '')
                doc = hit['_source']
                if "logo_thumbnail" in doc:
                    doc["logo_thumbnail"] = '{scheme}://{domain}{path}'.format(scheme=url.scheme, domain=url.netloc, path=doc["logo_thumbnail"])
                data.append(doc)

            # ----- format response ------
            response['count'] = cnt
            response['total_page'] = total_page

            # unlike DRF's pagination where urls of prev/next are returned,
            # for ES we only return page num for simplicity.
            response['prev'] = None if not page else page - 1
            response['next'] = None if page == total_page - 1 else page + 1

            response['results'] = data

        except Exception as e:
            # if ES failed. Use django's default way to search obj, which is very slow.
            logger.error("ES Failed on search query %s: %s" % (req_body, e))
            return Response({})
        return Response(response)


##########################
#   Clinic Detail APIs
##########################

class ClinicHome(generics.RetrieveUpdateAPIView):
    """
    get: get home page info for a particular clinic branch
    """
    name = 'clinic-home'
    queryset = ClinicProfile.objects.all()
    serializer_class = ClinicHomeSerializer
    lookup_field = 'uuid'
    permission_classes = [IsAdminOrReadOnly]


class ClinicDoctors(generics.RetrieveUpdateAPIView):
    """
    get: get doctor page info for a particular clinic (regardless of branch for now)
    """
    name = 'clinic-doctors'
    queryset = ClinicProfile.objects.all()
    serializer_class = ClinicDoctorsSerializer
    lookup_field = 'uuid'
    permission_classes = [IsAdminOrReadOnly]


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

# TODO: WIP
class ClinicSavedList(generics.ListAPIView):
    name = 'clinic-saved-list'
    serializer_class = ClinicPublicSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        #  TODO: not working
        user = self.request.user

        if not user:
            return []

        # for getting actions
        clinic_content_type = ContentType.objects.get(model='clinicprofile')

        saved_clinics = user.actor_actions.filter(action_object_content_type=clinic_content_type,
                                                  verb='save')
        unsaved_clinics = user.actor_actions.filter(action_object_content_type=clinic_content_type,
                                                    verb='unsave')

        saved_clinics = [item.action_object for item in saved_clinics]
        unsaved_clinics = [item.action_object for item in unsaved_clinics]

        # final saved clinics
        queryset = list(set(saved_clinics) - set(unsaved_clinics))

        # print("saved", saved_clinics)
        # print("unsaved", unsaved_clinics)
        # print("final queryset", queryset)

        return queryset


# TODO: WIP. NOT WORKING YET
class ClinicActionList(generics.ListAPIView):
    """
    get: get a list of saved clinic (on branch level) of a user.

    """
    name = 'case-action-list'
    serializer_class = ClinicSavedSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Overwrite. To get a list of clinic object that's saved by the request user.
        Note that we use action items instead of the built-in follow/unfollow,
        hence some extra handling here.

        :return:
        """
        user = self.request.user

        if not user:
            return []

        # for getting actions
        clinic_content_type = ContentType.objects.get(model='clinicprofile')

        # get list of saved actions, shouldn't have duplicate
        saved_cases = user.actor_actions.filter(action_object_content_type=clinic_content_type,
                                                verb='save')

        # get the action object
        queryset = []
        case_set = set()
        for item in saved_cases:
            if item not in case_set:
                queryset.append(item.action_object)

        return queryset

    def list(self, request):
        """
        Overwrite.
        # TODO: check page

        :param request:
        :return:
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        # print("page", page)
        serializer = self.get_serializer(page, many=True)

        # get clinic logos
        clinic_ids = set()
        for case in queryset:
            # corrupted data from
            if case is None:
                continue
            clinic_ids.add(case.clinic.uuid)

        clinic_objs = ClinicProfile.objects.filter(uuid__in=clinic_ids)
        logo_dict = {}

        for clinic in clinic_objs:
            logo_dict[clinic.uuid] = Base64ImageField().to_representation(clinic.logo_thumbnail_small)

        final_response = self.get_paginated_response(serializer.data)
        final_response.data['logos'] = logo_dict

        # TODO: else part
        return final_response


@api_view(['GET'])
def doctor_name_view(request, uuid='', clinic_name=''):
    """
    API view for returning a list of doctor names of
    a given clinic. Could specify the clinic by its
    uuid or by its name.

    uuid: clinic uuid
    clinic_name: clinic name
    :param request:
    :return: {'doctor': [list of doctor names]}
    """
    # print("uuid %s, clinic_name %s" % (uuid, clinic_name))

    # get clinic profile
    if uuid:
        clinic = get_object_or_None(ClinicProfile,
                                    uuid=uuid)
    elif clinic_name:
        clinic = get_object_or_None(ClinicProfile,
                                    display_name=clinic_name.strip())
    else:
        clinic = None

    if not clinic:
        return Response({'error': "clinic not found"},
                        status.HTTP_400_BAD_REQUEST)

    doctors = DoctorProfile.objects.filter(clinic_uuid=clinic.uuid)

    # TODO: can add doctor profile pic
    dedup = {}
    res = []

    for doctor in doctors:
        name = doctor.display_name.strip()
        if name not in dedup:
            res.append(name)
            dedup[name] = ''

    # res = [doctor.display_name.strip() for doctor in doctors]

    # clinic_uuid = request.query_params.get('uuid', '').strip()
    return Response({'doctors': res},
                    status.HTTP_200_OK)


@api_view(['POST'])
def like_unlike_clinic(request, clinic_uuid, flag='', do_like=True, actor_only=False, save_unsave=False):
    """
    DRF Funcional-based view to like/unlike or save/unsave a clinic (ClinicProfile, on branch level).
    Note that for each clinic, we'll at most have 1 activity object (like).
    Making a like API call when like is already the latest object will do no action.
    Making an unlike API call in the same situation will wipe out the previous like record.


    :param request: RESTful request.
    :param clinic_uuid: the target to be followed. (The model is ClinicProfile.)
    :param flag: -
    :param do_like: a flag so that both the follow and unfollow urls can
                      share this same view.
    :param actor_only: -
    :param save_unsave: boolean, determine like/unlike mode or save/unsave
    :return:
    """

    if not request.user.is_authenticated:
        logger.error('Unauthenticated user using like/unlike API.')
        # TODO: find default msg, think how to handle at client is more convenient
        return Response({'error': 'unauthenticated user'}, status.HTTP_401_UNAUTHORIZED)

    branch_id = request.query_params.get('branch_id', '')
    # print("branch id", branch_id)

    # get action object
    clinic_obj = get_object_or_None(ClinicProfile, uuid=clinic_uuid)

    if not clinic_obj:
        return Response({'error': 'invalid clinic id'}, status.HTTP_400_BAD_REQUEST)

    verb = 'save'

    # filter res to branch level. GKF queryset object
    res = clinic_obj.action_object_actions.filter(actor_object_id=request.user._id,
                                                  verb=verb,
                                                  data={'branch_id': branch_id}).order_by('-timestamp')

    if do_like:
        if res:
            if len(res) >= 2:
                # negative index not supported
                res[1:].delete()

            return Response({'succeed': 'duplicated %s action is ignored.' % verb}, status.HTTP_201_CREATED)

        action.send(request.user, verb=verb, action_object=clinic_obj, branch_id=branch_id)
        return Response({'succeed': ""}, status.HTTP_201_CREATED)
    else:
        if res:
            res.delete()
        return Response({'succeed': "redo %s" % verb}, status.HTTP_201_CREATED)
