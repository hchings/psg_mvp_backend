"""
API Views for Cases app.

"""

from collections import OrderedDict
import time

from annoying.functions import get_object_or_None
from actstream import actions, action

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from elasticsearch_dsl import Q
import coloredlogs, logging
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

from backend.settings import ES_PAGE_SIZE
from backend.shared.permissions import AdminCanGetAuthCanPost
from backend.shared.utils import add_to_cache, _prep_subcate
from users.clinics.models import ClinicProfile
from utils.drf.custom_fields import Base64ImageField
from .models import Case, CaseInviteToken
from .mixins import UpdateConciseResponseMixin
from .serializers import CaseDetailSerializer, CaseCardSerializer
from .doc_type import CaseDoc
from cases.management.commands.index_cases import Command

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

# for getting actions
case_content_type = ContentType.objects.get(model='case')

# TODO: WIP
# _prep_subcate()


# -------------------------------------------------------
#  For searching on cases or get a default list of cases
# -------------------------------------------------------


class CaseList(generics.ListCreateAPIView):
    """
    get: Return a list of posts with complete info.
    post: Create a new post. The uuid of the newly created case will be returned.
        - [Important] Although this view supports both JSON and Multipart,
                      please submit json and FormData payload separately.
          Reasoning: https://stackoverflow.com/questions/3938569/how-do-i-upload-a-file-with-metadata-using-a-rest-web-service

    """
    name = 'case-list'
    queryset = Case.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = CaseDetailSerializer
    permission_classes = [AdminCanGetAuthCanPost]

    def create(self, request, *args, **kwargs):
        """
        Customize Post Response to send back the id
        of newly created post.

        """
        logger.info("request data", request.data)  # should turned off
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # return the uuid of the newly created case.
        return Response({"id": serializer.data['uuid']},
                        status=status.HTTP_201_CREATED,
                        headers=headers)


# -------------------------------------------------------
#  For searching on cases or get a default list of cases
# -------------------------------------------------------


# Note the inherit order matters due to MRO.
class CaseDetailView(UpdateConciseResponseMixin,
                     generics.RetrieveUpdateDestroyAPIView):
    """
    get: Return a given case with complete info. (for edit a case)
    delete: Delete a given case.
    patch: Partially update a given case. (please use patch in frontend.)
    put: Entirely update a given case. (unused)

    # TODO: check multipart
    # TODO: add permission

    """
    name = 'case-detail'
    queryset = Case.objects.all()
    serializer_class = CaseDetailSerializer
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        """
        Overwrite retrieve method of RetrieveModelMixin.
        This is called on GET method to increment the
        number of view of this post.

        Two types of cache:
        - with and without edit query nparam

        """
        edit_mode = request.query_params.get("edit", False)
        if edit_mode:
            cache_key = "case_detail_edit_%s" % kwargs.get('uuid')
        else:
            cache_key = "case_detail_%s" % kwargs.get('uuid')

        data = cache.get(cache_key)
        if data:
            return Response(data)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        cache.set(cache_key, serializer.data)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """
        TODO: WIP
        Customize Patch Response to send back:
        # 1) img url (if the patch request contains update in ImageField)
        # 2) Empty (else)

        """

        # TODO: tmp, WIP
        other_imgs_list = []
        # TODO: WIP. very bad hard coded number.
        keys = request.data.keys() or []

        for key in keys:
            if key.startswith('other_imgs'):
                other_imgs_list.append({'img': request.data[key],
                                        'caption': ''})

        # print("other_imgs_list", other_imgs_list)
        if other_imgs_list:
            request.data['other_imgs'] = other_imgs_list

        # this will call UpdateConciseResponseMixin's method
        return self.partial_update(request, *args, **kwargs)


# -------------------------------------------------------
#  For searching on cases or get a default list of cases
# -------------------------------------------------------

class CaseSearchView(APIView):
    """
    Elasticsearch end point for Cases.
    ---
    An example of search query from frontend:

        {
            'keywords': [str1, str2, ...],  # can be keywords or clinic names, search in title too
            'gender': str
            'is_official': boolean
        }


    """
    name = 'case-search'
    # terms to remove from matc/multi-match query
    generic_terms = ['隆', '豐', '頭', '骨', '部', '墊', '雕塑', '矯正']

    # TODO: WIP, sort
    def post(self, request):
        """
        Return the search result.
        Search query should be specified in request body.
        Tiny clinic logos will be returned in a deticated field 'logos'.
        An example of search query from frontend:
        # TODO: add docstring. WIP

        {
            'title': 'some text',
            'is_official': True
        }

        :param request:
        :return:
        """

        # since this class does not inherit DRF's generics classes,
        # we need to prepare for the response data ourselves.
        response = OrderedDict({})

        # ----- parse request body -----
        req_body = request.data
        # print("request body for case search", req_body)

        try:
            # get page num from url para.
            # page number starts from 0.
            page = int(request.query_params.get('page', 0))

            # check cache
            # use q combined + page number as cache key
            # should open below five TODO
            cache_key = '_'.join(['case_search', str(sorted(req_body.items())), str(page)]).replace(" ", "")
            logger.info("cache key: %s" % cache_key)
            data = cache.get(cache_key)
            if data:
                return Response(data)

            q_combined = None
            if req_body:
                # 1. check surgeries col
                surgeries = req_body.get('surgeries', [])
                # If it's a defined surgery tag, we don't search on clinic name
                if surgeries:
                    q_surgeries = None
                    for item in surgeries:
                        # give more weight on 'surgeries' field
                        # hard-coded words that I don't want to trigger in search
                        q_new = Q("match_phrase",
                                  surgeries=item)
                        if '唇' in item:
                            # TODO: this is a bad hacky way to not show 豐唇 and 縮唇 in the same result
                            q_new_2 = Q("match_phrase",
                                        title=item)
                        else:
                            item_cleaned = item
                            for word in self.generic_terms:
                                item_cleaned = item_cleaned.replace(word, '')

                            # expand the search on title fields
                            q_new_2 = Q("multi_match",
                                        query=item_cleaned,
                                        fields=["surgeries^2", "title"])
                        q_surgeries = (q_new | q_new_2) if not q_surgeries else q_surgeries | q_new | q_new_2

                    q_combined = q_surgeries

                # 2. check other col, which stores undefined tags (free-text)
                others = req_body.get('others', [])
                # OR on all other search query
                # TODO: WIP
                if others:
                    q_others = None
                    for item in others:
                        # give more weight on 'surgeries' field
                        q_new = Q("multi_match",
                                  query=item,
                                  fields=["surgeries^2", "title", "clinic_name"])
                        # q_new = Q("match",
                        #           query=item,
                        #           fields=["surgeries"],
                        #           fuzziness=5)
                        q_others = q_new if not q_others else q_others | q_new
                        # print("chain oth, ", q_new)

                    q_combined = q_others if not q_combined else q_combined | q_others

            if q_combined is None:
                q_combined = Q({"match_all": {}})

            # check
            if page == 0 and not req_body:
                # worst case
                if Command.ensure_index_exist():
                    time.sleep(1)
                    CaseDoc.init()

            s = CaseDoc.search(index='cases')  # specify search DocType

            # add ES query, and only return the id field
            s = s.query(q_combined).source(includes=['id'])

            # add filters, note to use "term" instead of "match"
            if 'is_official' in req_body:
                s = s.filter('term', is_official=req_body['is_official'] or False)

            if req_body.get('gender', ''):
                s = s.filter('term', gender=req_body['gender'])

            cnt = s.count()  # get number of hits
            total_page = cnt // ES_PAGE_SIZE + 1

            if page >= total_page:
                return Response({'error': 'exceeds page num.'})

            # Only take minimum number of records that you need for this page from ES by slicing
            res = s[page * ES_PAGE_SIZE: min((page + 1) * ES_PAGE_SIZE, cnt)].execute()
            response_dict = res.to_dict()

            # print("get result", response_dict)

            hits = response_dict['hits']['hits']

            data, ids = [], []
            data_dict = {}  # for storing an Q(1) mapping from id to source document
            for hit in hits:
                hit['_source']['score'] = hit.get('_score', '')
                doc = hit['_source']
                # doc.pop('open_sunday')
                data.append(doc)
                ids.append(int(hit['_source']['id']))
                data_dict[hit['_source']['id']] = data[-1]

            # get the corresponding objects from mongo.
            # however, Django ORM returns the results in a different order,
            # but it doesn't matter as I only need to get the logos.
            queryset = Case.objects.filter(uuid__in=ids)

            # ids = [hit['_source']['id'] for hit in hits]
            # queryset = Skill.objects.filter(id__in=ids)
            case_list = list(queryset)
            case_list.sort(key=lambda case: ids.index(case.uuid))
            # [Important!] Must pass in the context to get the full media path.
            # Pass in 'seach_view' for Memcached wildcard invalidation
            serializer = CaseCardSerializer(case_list, many=True, context={'request': request}, search_view=True)

            # get clinic tiny logos
            # TODO: some redundancy here
            clinic_ids = []
            for case in case_list:
                try:
                    c_id = case.clinic.uuid
                    clinic_ids.append(c_id)
                except AttributeError as e:
                    logger.error("CaseSearchView error: %s" % e)

            # TODO: WIP
            queryset = ClinicProfile.objects.filter(uuid__in=clinic_ids)

            # add back info that are not stored in ES engine.
            # since there are only a few fields. It's faster to skip serializer.
            logo_dict = {}
            for clinic in queryset:
                if clinic.uuid not in logo_dict:
                    logo_dict[clinic.uuid] = Base64ImageField().to_representation(clinic.logo_thumbnail_small)

            # ----- format response ------
            response['count'] = cnt
            response['total_page'] = total_page

            # unlike DRF's pagination where urls of prev/next are returned,
            # for ES we only return page num for simplicity.
            response['prev'] = None if not page else page - 1
            response['next'] = None if page == total_page - 1 else page + 1

            response['results'] = serializer.data
            response['logos'] = logo_dict
            # response['logos'] = {}

            # only set cache if success
            add_to_cache(cache_key, response, True)
            cache.set(cache_key, response)

        except Exception as e:
            # if ES failed. Use django's default way to search obj, which is very slow.
            logger.error("ES Failed on search cases with query %s: %s" % (req_body, e))
            cases = Case.objects.all()
            serializer = CaseCardSerializer(cases, many=True,
                                            search_view=True)  # TODO: WIP. need better error handling.
            # TODO: WIP
            return Response({})

        return Response(response)


# -------------------------------------------------------------------
#  Case Manage - for getting a list of cases of authenticated users.
# -------------------------------------------------------------------

class CaseManageListView(generics.ListAPIView):
    """
    get: Return a list of all cases of an authenticated user with brief info.

    """
    name = 'case-manage-list'
    queryset = Case.objects.all()
    serializer_class = CaseCardSerializer
    permission_classes = [IsAuthenticated]

    # TODO: check better way for this.
    # TODO: as this is called while code is ini and while user request, which is duplicated.
    def get_queryset(self, *args, **kwargs):
        # get query parameter
        req = self.request
        state = req.query_params.get('state') or ''

        # check whether is superuser
        is_superuser = self.request.user.is_superuser

        if is_superuser:
            # superuser can see all posts.
            return Case.objects.filter(state=state).order_by('-posted')
        else:
            # if not user, the response will just be empty.
            # Put the recent one on the top.
            return Case.objects.filter(author={'uuid': str(self.request.user.uuid)},
                                       state=state).order_by('-posted')


class CaseActionList(generics.ListAPIView):
    """
    get: get a list of saved cases of a user.

    """
    name = 'case-action-list'
    serializer_class = CaseCardSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Overwrite. To get a list of case object that's saved by the request user.
        Note that we use action items instead of the built-in follow/unfollow,
        hence some extra handling here.

        :return:
        """
        user = self.request.user

        if not user:
            return []

        # get list of saved actions, shouldn't have duplicate
        saved_cases = user.actor_actions.filter(action_object_content_type=case_content_type,
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
        # pass extra parameter when creating the serializer instance.
        # The search_view param will decide which fields to return
        serializer = self.get_serializer(page, many=True, search_view=True)

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


@api_view(['POST'])
def like_unlike_case(request, case_uuid, flag='', do_like=True, actor_only=False, save_unsave=False):
    """
    DRF Funcional-based view to like or unlike a case.
    Note that for each case, we'll at most have 1 activity object (like).
    Making a like API call when like is already the latest object will do no action.
    Making an unlike API call in the same situation will wipe out the previous like record.


    :param request: RESTful request.
    :param case_uuid: the target to be followed. (The model is Case.)
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

    # get action object
    case_obj = get_object_or_None(Case, uuid=case_uuid)

    if not case_obj:
        return Response({'error': 'invalid comment id'}, status.HTTP_400_BAD_REQUEST)

    verb = 'save' if save_unsave else 'like'

    res = case_obj.action_object_actions.filter(actor_object_id=request.user._id, verb=verb).order_by('-timestamp')

    if do_like:
        if res:
            return Response({'succeed': 'duplicated %s action is ignored.' % verb}, status.HTTP_201_CREATED)

        # else
        if len(res) >= 2:
            # negative index not supported
            res[1:].delete()

        action.send(request.user, verb=verb, action_object=case_obj)
        return Response({'succeed': ""}, status.HTTP_201_CREATED)
    else:
        if res:
            res.delete()
        return Response({'succeed': "redo %s" % verb}, status.HTTP_201_CREATED)


# -------------------------------------------------------------------
#  Case Invite - for inviting other users to write case TODO: WIP
# -------------------------------------------------------------------


class CaseInviteTokenGenView(generics.RetrieveAPIView):
    name = 'case-invite-gen'
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # try to get token
        token = get_object_or_None(CaseInviteToken, user_uuid=request.user.uuid)

        if not token:
            # assume is required
            username = request.user.username

            if not username:
                # TODO: bad
                username = request.user.email.split('@')[0]

            username = username.lower().replace(' ', '') + str(request.user.uuid)[:3]

            token = CaseInviteToken(user_code=username, user_uuid=request.user.uuid)
            token.save()

        return Response({'referral_user': token.user_code,
                         'referral_token': token.token}, status.HTTP_200_OK)


class CaseInviteInfoDetail(generics.RetrieveAPIView):
    """
    TODO: you can add in more info if you want.
    """
    name = 'case-invite-info'

    def get(self, request):
        user_code = request.query_params.get("userCode", False)
        invite_token = request.query_params.get("token", False)

        # try to get token
        token = get_object_or_None(CaseInviteToken,
                                   user_code=user_code,
                                   token=invite_token)

        if not token:
            return Response({'error': 'invalid token'}, status.HTTP_400_BAD_REQUEST)


        inviter_user_obj = get_object_or_None(get_user_model(), uuid=token.user_uuid)

        if inviter_user_obj:
            username = inviter_user_obj.username.title()
        else:
            username = ''

        return Response({'inviter': username}, status.HTTP_200_OK)
