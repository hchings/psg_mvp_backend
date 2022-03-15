"""
DRF Serializers for clinics.

"""
from random import randint
import coloredlogs, logging
from collections import OrderedDict

from rest_framework import serializers
from utils.drf.custom_fields import Base64ImageField

from reviews.models import Review
from reviews.serializers import ReviewSerializer
from cases.models import Case
from cases.serializers import CaseCardSerializer
from users.doctors.models import DoctorProfile
from users.doctors.serializers import DoctorDetailSerializer
from users.clinics.models import ClinicBranch
from backend.settings import ROOT_URL
from .models import ClinicProfile


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class ClinicPublicSerializer(serializers.HyperlinkedModelSerializer):
    """
    Read only Serializer for showing Clinic information.
    Most of the information are from ClinicProfile.

    """
    uuid = serializers.ReadOnlyField()
    logo_thumbnail = serializers.ImageField(max_length=None,
                                            use_url=True,
                                            required=False)
    # nested field
    services_raw = serializers.ListField()  # TODO: use this to make list
    saved_by_user = serializers.SerializerMethodField(required=False)
    BRANCH_KEYS_INCLUDED = set(['place_id', 'branch_name', 'is_head_quarter', 'address', 'region', 'locality'])

    def get_branches(self, obj):
        """
        To serialize ArrayModelField from djongo.
        :param obj:
        :return:
        """
        if type(obj.branches) == list:
            embedded_list = []
            for item in obj.branches:
                embedded_dict = item.__dict__
                for key in list(embedded_dict.keys()):
                    if key.startswith('_') or key not in self.BRANCH_KEYS_INCLUDED:
                        embedded_dict.pop(key)
                    # TODO: tmp fix. PhoneNumber package has bug and is not JSON serializable
                    # https://github.com/stefanfoulis/django-phonenumber-field/issues/225
                    # elif key == 'phone':
                    #     embedded_dict[key] = str(embedded_dict[key])
                    # elif key == 'opening_info':
                    #     # restore the list structure
                    #     # reason: Djongo abstract model couldn't use ListField..
                    #     embedded_dict[key] = [] if not embedded_dict[key] \
                    #         else ast.literal_eval(embedded_dict[key])

                embedded_list.append(embedded_dict)
            return_data = embedded_list
        else:
            embedded_dict = obj.branches
            for key in list(embedded_dict.keys()):
                if key.startswith('_'):
                    embedded_dict.pop(key)
                # TODO: tmp as above
                elif key == 'phone':
                    embedded_dict[key] = str(embedded_dict[key])

            return_data = embedded_dict
        return return_data

    # TODO: WIP
    def get_saved_by_user(self, obj):
        """
        Return a boolean flag indicating whether the user
        in the request saved the current clinic.

        For unauthorized users, it will always be false.

        :param obj: the comment object
        :return (boolean):
        """
        request = self.context.get('request', None)

        # for unlogin user
        if not request or request.user.is_anonymous:
            return False

        # it should only have one obj if it's saved
        action_objs = obj.action_object_actions.filter(actor_object_id=request.user._id, verb='save')

        return False if not action_objs else True

    # def get_concise_regions(self, obj):
    #     """
    #     Truncate the ugly 市/縣 words and
    #     remove duplicates.
    #
    #     :param obj: an User object.
    #     :return (string[]): an array of regions
    #
    #     """
    #     d = {}
    #     concise_regions = []
    #     for branch in obj.clinic_profile.branches.all():
    #         # TODO: rewrite the reg
    #         region = branch.region
    #         # alternative is no region
    #         # TODO: bad
    #         if not region and len(branch.branch_name) == 3:
    #             region = branch.branch_name
    #
    #         # truncate
    #         if region and (region.endswith('市')
    #                        or region.endswith('縣')
    #                        or region.endswith('店')):
    #             region = region[:-1]
    #
    #         # remove duplicate
    #         if region and region not in d:
    #             concise_regions.append(region)
    #             d[region] = ''
    #
    #     return concise_regions

    # def get_opening_info(self, obj):
    #     # TODO: deal with empty case
    #     for branch in obj.clinic_profile.branches.all():
    #         if branch.is_head_quarter:
    #             if branch.opening_info:
    #                 return json.loads(branch.opening_info)
    #     return {}

    # def get_case_num(self, obj):
    #     """
    #     Get the number of cases(i.e., posts) that belonged
    #     to this clinic. (default function name for field case_num)
    #
    #     :param obj: an User object
    #     :return (int): reverse foreignkey objects number
    #     """
    #     return obj.clinic_user_posts.count()

    # def get_rating(self, obj):
    #     """
    #     Since in google MAP API, only a location (i.e., a ClinicBranch)
    #     has a rating. So for a Clinic User, we simply average
    #     the ratings from all its branches.
    #
    #     :param obj: an User object
    #     :return (float): the averaged ratings
    #     """
    #     branch_ratings = [branch.rating for branch in obj.branches.all()
    #                       if branch.rating]
    #     # arithmetic average rounded to 1 decimal point
    #     return 0.0 if not branch_ratings else round(sum(branch_ratings)/len(branch_ratings), 1)

    class Meta:
        model = ClinicProfile
        fields = ('uuid', 'display_name', 'logo_thumbnail', 'website_url', 'fb_url',
                  'line_url', 'services_raw', 'instagram_url',
                  'branches', 'saved_by_user')

    def __init__(self, *args, **kwargs):
        """
        Dynamically change field.
        :param args:
        :param kwargs:
        """
        super(ClinicPublicSerializer, self).__init__(*args, **kwargs)
        if self.context['request'].method in ['POST', 'PUT', 'PATCH']:
            # nested fields don't have serializers implicitly assigned
            self.fields['branches'] = BranchSerializer(required=False, many=True)
        else:
            self.fields['branches'] = serializers.SerializerMethodField()

    def create(self, validated_data):
        raise NotImplementedError("Does not allow create a ClinicProfile through API atm.")

    def update(self, instance, validated_data):
        """
        Need this to handle noSQL record creation (not natively supported by Django).
        In ClinicProfile, "branches" and "serice_raw" are using abstract Djongo schemas
        and need to be handled.
        :param instance:
        :param validated_data:
        :return:
        """
        in_branches = [] if 'branches' not in validated_data else validated_data.pop('branches')
        # TODO: Not done yet
        in_services_raw = [] if 'services_raw' not in validated_data else validated_data.pop('services_raw')

        if in_services_raw and isinstance(in_services_raw, list):
            # if we are letting the front end send the full list that is easiest.
            instance.services_raw = in_services_raw

        if in_branches and isinstance(in_branches, list):
            place_id_to_branch = OrderedDict([(branch.place_id, branch) for branch in (instance.branches or []) \
                                              if branch.place_id])
            for in_branch in in_branches:
                # if place_id matches an existing branch
                if "place_id" in in_branch and in_branch["place_id"] in place_id_to_branch:
                    target_branch = place_id_to_branch[in_branch["place_id"]]
                    for k, v in in_branch.items():
                        if hasattr(target_branch, k):
                            setattr(target_branch, k, v)
                else:
                    # create a new branch obj
                    logger.info("No matched branch, creating a new one...")
                    serializer = BranchSerializer(data=in_branch)
                    if serializer.is_valid():
                        target_branch = ClinicBranch(**serializer.validated_data)
                        # assume place_id is required
                        place_id_to_branch[target_branch.place_id] = target_branch
                        # print("new target_branch", target_branch, serializer.validated_data)
                    else:
                        logger.error("ClinicPublicSerializer Invalid branch %s " % str(in_branch))
            instance.branches = list(place_id_to_branch.values())

        # will call save()
        super(ClinicPublicSerializer, self).update(instance, validated_data)
        return instance


class BranchSerializer(serializers.Serializer):
    branch_name = serializers.CharField(required=False)
    # place_id = serializers.ReadOnlyField(required=False)
    place_id = serializers.CharField(required=True)  # TODO: double check
    is_head_quarter = serializers.BooleanField(required=False)
    opening_info = serializers.CharField(required=False)
    rating = serializers.FloatField(required=False)
    address = serializers.CharField(required=False)
    address_help_text = serializers.CharField(required=False)
    region = serializers.CharField(required=False)
    locality = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)


class ClinicHomeSerializer(serializers.HyperlinkedModelSerializer):
    """
    Read only Serializer for clinic home url.

    """
    uuid = serializers.ReadOnlyField()
    logo_thumbnail = Base64ImageField()  # unsure, kinda large, maybe an URL is better
    branch_info = serializers.SerializerMethodField(required=False)
    saved_by_user = serializers.SerializerMethodField(required=False)
    services = serializers.SerializerMethodField(required=False)
    reviews = serializers.SerializerMethodField(required=False)
    cases = serializers.SerializerMethodField(required=False)

    # is_head_quarter = serializers.SerializerMethodField(required=False)

    class Meta:
        model = ClinicProfile
        fields = ('website_url', 'uuid', 'display_name', 'services', 'branch_info',
                  'saved_by_user', 'reviews', 'cases', 'logo_thumbnail')

    # should we add is_head_quarter ?
    def get_branch_info(self, obj):
        request = self.context.get('request', None)
        branch_id = request.query_params.get('branch_id', '')

        # TODO: should I assume it's HQ?
        if not branch_id:
            return ''

        # find the right branch
        for branch in obj.branches or []:
            if branch.branch_id == branch_id:
                serializer = BranchSerializer(branch)
                return serializer.data

        # TODO: assumption: data check is in place
        return ''

    # TODO: tmp for now. need normalization
    def get_services(self, obj):
        tokens = obj.services_raw or []
        # tokens
        return ['雙眼皮', '隆鼻', '削骨'] * 3

    # TODO: move out.
    def get_saved_by_user(self, obj):
        """
        Return a boolean flag indicating whether the user
        in the request saved the current clinic.

        For unauthorized users, it will always be false.

        :param obj: the comment object
        :return (boolean):
        """
        # TODO: WIP
        return False
        # request = self.context.get('request', None)
        #
        # # print("reauest", request)
        #
        # # for unlogin user
        # if not request or request.user.is_anonymous:
        #     return False
        #
        # # it should only have one obj if it's saved
        # action_objs = obj.action_object_actions.filter(actor_object_id=request.user._id, verb='save')
        # # for item in action_objs:
        # #     print("branch_id", item.data['branch_id'])
        #
        # # logger.info("action_objs in serializer %s" % action_objs)
        #
        # return False if not action_objs else True

    def get_reviews(self, obj):
        request = self.context.get('request', None)
        branch_id = request.query_params.get('branch_id', '')

        # TODO: should I assume it's HQ?
        if not branch_id:
            return {}  # TODO: not too good

        # find the right branch
        # TODO: pagination
        for branch in obj.branches or []:
            if branch.branch_id == branch_id:
                reviews = Review.objects.filter(clinic={'place_id': branch.place_id})
                serializer = ReviewSerializer(reviews,
                                              many=True,
                                              context={'request': self.context['request']})
                return {"count": len(reviews), "results": serializer.data}
                # return {"branch_name": branch.branch_name,
                #         "rating":branch.rating}

        # TODO: assumption: data check is in place
        return {}

    def get_cases(self, obj):
        """
        TODO: WIP
        :param obj:
        :return:
        """
        cases = Case.objects.filter(clinic={'uuid': obj.uuid},
                                    state="published").order_by('-interest')
        if not cases:
            return {}
        elif len(cases) > 1:
            chosen_case = cases[randint(0, len(cases) - 1)]
        else:
            chosen_case = cases[0]

        serializer = CaseCardSerializer(chosen_case,
                                        many=False,
                                        context={'request': self.context['request']})

        # return an array, in case we need to return multiple cases in the future
        return {"count": len(cases),
                "results": [serializer.data]}


# TODO: WIP
class ClinicDoctorsSerializer(serializers.HyperlinkedModelSerializer):
    """
    Read only Serializer for clinic doctor tab.
    """

    doctors = serializers.SerializerMethodField(required=False)

    # can add map data
    class Meta:
        model = ClinicProfile
        fields = ('uuid', 'doctors')

    def get_doctors(self, obj):
        doctors = DoctorProfile.objects.filter(clinic_uuid=obj.uuid)
        serializer = DoctorDetailSerializer(doctors,
                                            many=True,
                                            context={'request': self.context['request']})
        return {"count": len(doctors),
                "results": serializer.data}


class ClinicCardSerializer(serializers.HyperlinkedModelSerializer):
    """
    Read only Serializer for clinic brief info.

    """
    uuid = serializers.ReadOnlyField()
    services = serializers.SerializerMethodField(required=False)
    regions = serializers.SerializerMethodField(required=False)
    num_cases = serializers.SerializerMethodField(required=False)
    # to return the human readable value in ChoiceField
    biz_type = serializers.CharField(source='get_biz_type_display')

    class Meta:
        model = ClinicProfile
        fields = ('uuid', 'display_name', 'logo_thumbnail', 'regions', 'num_cases', 'services', 'biz_type')

    def __init__(self, *args, **kwargs):
        self.indexing_algolia = kwargs.get("indexing_algolia", False)
        # self.allow_fields = kwargs.get("allow_fields", False)

        # downstream can't accept this keyword
        if self.indexing_algolia:
            kwargs.pop('indexing_algolia')

        # if self.allow_fields:
        #     kwargs.pop('allow_fields')

        super(ClinicCardSerializer, self).__init__(*args, **kwargs)

        if self.indexing_algolia:
            self.fields['objectID'] = serializers.SerializerMethodField(required=False)

        if not self.context.get('request', None):
            self.fields['logo_thumbnail'] = serializers.SerializerMethodField()

        # if self.allow_fields and isinstance(self.allow_fields, list):
        #     print("set fields", self.allow_fields)
        #     self.fields = self.allow_fields


    def get_objectID(self, obj):
        return str(obj.uuid)

    def get_logo_thumbnail(self, obj):
        return "" if not obj.logo_thumbnail else ROOT_URL + obj.logo_thumbnail.url

    def get_services(self, obj):
        return obj.services_raw or []

    def get_regions(self, obj):
        dedup = {}
        regions = []
        for branch in obj.branches:
            region = branch.region
            if region and region not in dedup and (region.endswith('市') or region.endswith('縣')):
                regions.append(region)
        return regions

    def get_num_cases(self, obj):
        return Case.objects.filter(clinic={'uuid': obj.uuid},
                                   state="published").count()



# TODO: WIP
class ClinicSavedSerializer(serializers.HyperlinkedModelSerializer):
    """
    Read only Serializer for showing Clinic information.
    Most of the information are from ClinicProfile.

    """

    branch_name = serializers.SerializerMethodField(required=False)

    class Meta:
        model = ClinicProfile
        fields = ('website_url', 'uuid', 'user_id', 'display_name', 'logo_thumbnail')

    def get_branch_name(self, obj):
        return ''


class ClinicProfileSerializer(serializers.HyperlinkedModelSerializer):
    
    display_name = serializers.CharField(max_length=30, required=False)
    logo = serializers.ImageField(max_length=None,
                                            use_url=True,
                                            required=False)
    logo_thumbnail = serializers.ImageField(max_length=None,
                                            use_url=True,
                                            required=False)
    logo_thumbnail_small = serializers.ImageField(max_length=None,
                                            use_url=True,
                                            required=False)
    services = serializers.SerializerMethodField(required=False)

    class Meta:
        model = ClinicProfile
        fields = ('uuid','display_name','logo','logo_thumbnail','logo_thumbnail_small','phone','website_url','fb_url','line_url','instagram_url','pixnet_url','line_id', 'customer_email', 'branches','services')

    def get_services(self, obj):
        return obj.services_raw or []
    
    def save_image_from_data(self):
        # Regenerate thumbnail
        self.logo.generate(force=True)
        return True
    

class AddBranchSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        # abstract = True
        model = ClinicBranch    
        fields = ('place_id','branch_name')  
         