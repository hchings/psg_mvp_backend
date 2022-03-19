"""
DRF Views for clinics.

"""
import coloredlogs, logging
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from annoying.functions import get_object_or_None
from actstream import actions, action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from django.contrib.contenttypes.models import ContentType

from backend.shared.permissions import IsAdminOrReadOnly, IsAdminOrIsClinicOwner
from utils.drf.custom_fields import Base64ImageField
from users.doctors.models import DoctorProfile
from .serializers import ClinicPublicSerializer, ClinicSavedSerializer, \
    ClinicHomeSerializer, ClinicDoctorsSerializer, ClinicProfileSerializer
from .models import ClinicProfile, ClinicBranch

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class ClinicPublicList(generics.ListAPIView):
    """
    get: get a list of info of all the clinics.

    """
    name = 'clinicpublic-list'
    queryset = ClinicProfile.objects.all()
    serializer_class = ClinicPublicSerializer


class ClinicPublicDetail(generics.RetrieveUpdateAPIView):
    """
    get: Return the info of a clinic of given uuid.

    """
    name = 'clinicpublic-detail'
    queryset = ClinicProfile.objects.all()
    serializer_class = ClinicPublicSerializer
    lookup_field = 'uuid'
    permission_classes = [IsAdminOrIsClinicOwner]

    def get_object(self):
        obj = super().get_object()
        return obj

    def put(self, request, uuid, *args, **kwargs):
        place_id_to_delete = request.data.get('place_id_to_delete', None)
        place_id = request.data.get('place_id', None)
        branch_name = request.data.get('branch_name', None)
        profile_obj = self.get_object()

        # Delete a branch :--
        if place_id_to_delete is not None and profile_obj.branches:
            for i in range(len(profile_obj.branches)):
                if str(profile_obj.branches[i]) == place_id_to_delete:
                    profile_obj.branches.pop(i)
                    profile_obj.save()
                    return Response({"message": f"Branch deleted:{place_id_to_delete}"}, status=status.HTTP_200_OK)

            return Response({"message": "Invalid place_id"}, status.HTTP_400_BAD_REQUEST)

        # Create a branch:--
        if place_id is not None:
            try:
                # check branch existence
                try:
                    ClinicProfile.objects.get(uuid=uuid, branches={'place_id': f'{place_id}'})
                    return Response({'error': "branch %s already exist" % place_id},
                                    status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    # object not exist
                    pass

                branch = ClinicBranch(branch_name=branch_name, place_id=place_id)
                profile_obj.branches.append(branch)
                profile_obj.save()
                serializer = ClinicPublicSerializer(profile_obj,
                                                    context={'request': request},
                                                    fields=['branches'])
                logger.info("branch created for clinic %s" % uuid)
                return Response(serializer.data)
            except Exception as e:
                logger.error("Error when creating a branch for clinic %s: %s" % (uuid, str(e)))
                return Response({'error': "clinic not found"},
                                status.HTTP_400_BAD_REQUEST)

        # Update:--
        try:
            serializer = ClinicProfileSerializer(profile_obj, data=request.data)
            if serializer.is_valid():
                serializer.save()
                serializer = ClinicPublicSerializer(profile_obj, context={'request': request})
                return Response(serializer.data)
        except:
            return Response({"message":"Invalid uuid"},status.HTTP_400_BAD_REQUEST)


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
