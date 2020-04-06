"""
API Views for Cases app.

"""

from collections import OrderedDict

from rest_framework import generics, permissions, status
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from elasticsearch_dsl import Q
import coloredlogs, logging

from backend.settings import ES_PAGE_SIZE
from users.clinics.models import ClinicProfile
from utils.drf.custom_fields import Base64ImageField
from .models import Case
from .mixins import UpdateConciseResponseMixin
from .serializers import CaseDetailSerializer, CaseCardSerializer
from .doc_type import CaseDoc

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


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

    # permission_classes = (OwnerCanCreateOrReadOnly, )

    def retrieve(self, request, *args, **kwargs):
        """
        Overwrite retrieve method of RetrieveModelMixin.
        This is called on GET method to increment the
        number of view of this post.

        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """
        TODO: WIP
        Customize Patch Response to send back:
        # 1) img url (if the patch request contains update in ImageField)
        # 2) Empty (else)

        """

        # print("patch data 0", request.data)
        # request.data = dict(request.data)

        # TODO: tmp, WIP
        other_imgs_list = []
        # TODO: WIP
        for i in range(0, 6):
            key = 'other_imgs' + str(i)
            if key not in request.data:
                break
            other_imgs_list.append({'img': request.data[key],
                                    'caption': ''})

        print("other_imgs_list", other_imgs_list)
        if other_imgs_list:
            request.data['other_imgs'] = other_imgs_list

        # request.data['other_imgs'] = [{'caption': '1'},
        # {'caption': '2'}]
        # request.data['other_imgs'] = [request.data['other_imgs0']]

        # 'img': request.data['other_imgs0'],
        # request.data['other_imgs'] = ['1', ' 2', '3']

        # request.data['title'] = 'wer'
        # request.data = {'other_imgs': [OrderedDict([('caption', '123')])]}

        # print("patch data", request.data, type(request.data), type(request.data['other_imgs']),
        #       request.data['other_imgs'][0], type(request.data['other_imgs'][0]))

        # this will call UpdateConciseResponseMixin's method
        return self.partial_update(request, *args, **kwargs)


# -------------------------------------------------------
#  For searching on cases or get a default list of cases
# -------------------------------------------------------

class CaseSearchView(APIView):
    """
    Elasticsearch end point for Cases.
    ---
    parameters:
        # TODO: add docstring

    """
    name = 'case-search'

    # TODO: WIP
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

        # TODO: return all for now.
        q_combined = Q({"match_all": {}})

        try:
            # get page num from url para.
            # page number starts from 0.
            page = int(request.query_params.get('page', 0))
            s = CaseDoc.search(index='cases')  # specify search DocType
            s = s.query(q_combined)  # add ES query
            cnt = s.count()  # get number of hits
            total_page = cnt // ES_PAGE_SIZE + 1

            if page >= total_page:
                return Response({'error': 'exceeds page num.'})

            # Only take minimum number of records that you need for this page from ES by slicing
            res = s[page * ES_PAGE_SIZE: min((page + 1) * ES_PAGE_SIZE, cnt)].execute()
            response_dict = res.to_dict()
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
            serializer = CaseCardSerializer(case_list, many=True, context={'request': request})

            # get clinic tiny logos
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

        except Exception as e:
            # if ES failed. Use django's default way to search obj, which is very slow.
            logger.error("ES Failed on search cases with query %s: %s" % (req_body, e))
            cases = Case.objects.all()
            serializer = CaseCardSerializer(cases, many=True)  # TODO: WIP. need better error handling.
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
        # logger.info("auth:", self.request.user.is_authenticated, self.request.user.uuid, type(self.request.user.uuid),
        #       self.request.user.username)

        # if not user, the response will just be empty.
        # Put the recent one on the top.
        return Case.objects.all().filter(author={'uuid': str(self.request.user.uuid)}).order_by('-posted')
