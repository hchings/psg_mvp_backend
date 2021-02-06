"""
REST Framework Serializers for Case app.

"""
import ast
from rest_framework import serializers, exceptions
from drf_extra_fields.fields import Base64ImageField
from bson import ObjectId
from annoying.functions import get_object_or_None
import coloredlogs, logging
from hitcount.models import HitCount

from django.db.models import Q

from backend.shared.fields import embedded_model_method
from backend.shared.serializers import AuthorSerializer
from backend.shared.utils import image_as_base64
from .models import Case, CaseImages, UserInfo, ClinicInfo, SurgeryMeta, SurgeryTag
from rest_framework.fields import (  # NOQA # isort:skip
    CreateOnlyDefault, CurrentUserDefault, SkipField, empty
)

# TODO: this dependency is not good
from comments.models import Comment
from comments.serializers import CommentSerializer
from comments.views import COMMENT_PAGE_SIZE
from users.clinics.models import ClinicProfile

# from users.clinics.serializers import ClinicLogoSerializer
# COMMENT_PAGE_SIZE

# from rest_framework.exceptions import ErrorDetail, ValidationError
# from rest_framework.serializers import  as_serializer_error
# from django.core.exceptions import ValidationError as DjangoValidationError
# from rest_framework.fields import get_error_detail, set_value
# from collections import OrderedDict
# from collections.abc import Mapping
# from rest_framework.utils import html, humanize_datetime, json, representation

# Create a logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class ClinicLogoSerializer(serializers.HyperlinkedModelSerializer):
    logo_thumbnail_small = serializers.ImageField(max_length=None,
                                                  use_url=True,
                                                  required=False)

    # too large the payload
    # logo_thumbnail_small = Base64ImageField()

    class Meta:
        model = ClinicProfile
        fields = ('uuid', 'logo_thumbnail_small')


#########################################################
#    Field Serializers for djongo's EmbeddedModelField
#    This will handle post?
#########################################################


class ClinicInfoSerializer(serializers.Serializer):
    """
    Serializer for clinic field.
    """
    display_name = serializers.CharField(required=False, allow_blank=True)
    branch_name = serializers.CharField(required=False, allow_blank=True)
    doctor_name = serializers.CharField(required=False, allow_blank=True)
    place_id = serializers.ReadOnlyField()
    uuid = serializers.ReadOnlyField()


class ClinicInfoURLSerializer(serializers.Serializer):
    """
    Serializer for clinic field.
    This is because the current mvp has no clinic pages yet.
    """
    display_name = serializers.CharField(required=False, allow_blank=True)
    doctor_name = serializers.CharField(required=False, allow_blank=True)
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        display_name = obj.display_name

        if display_name:
            clinic_obj = get_object_or_None(ClinicProfile, display_name=display_name)
            if clinic_obj:
                return clinic_obj.website_url

        return ''


class ClinicInfoBriefSerializer(serializers.Serializer):
    """
    Serializer for clinic field.
    """
    display_name = serializers.ReadOnlyField()
    uuid = serializers.ReadOnlyField()


class SurgeryMetaSerializer(serializers.Serializer):
    """
    Serializer for surgery_meta field.
    """
    year = serializers.IntegerField(required=False, min_value=0)
    month = serializers.IntegerField(required=False, min_value=1)
    min_price = serializers.IntegerField(required=False, min_value=0)
    max_price = serializers.IntegerField(required=False, min_value=0)


class SurgeryTagSerializer(serializers.Serializer):
    """
    Serializer for surgeries field.
    """
    name = serializers.CharField(required=False, allow_blank=True)
    mat = serializers.CharField(required=False, allow_blank=True)


######################################
#     Card-view (brief) Serializers
######################################

class CaseStatsSerializer(serializers.ModelSerializer):
    # number
    like_num = serializers.SerializerMethodField(required=False)

    view_num = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Case
        fields = ('like_num', 'view_num', 'uuid')

    def get_like_num(self, obj):
        """
        Return how many distinct users liked this case.

        :param obj:
        :return:
        """
        try:
            return len(obj.action_object_actions.filter(verb='like'))
        except Exception as e:
            print("errir get liked num", obj.uuid)
            return 0

    def get_view_num(self, obj):

        try:
            hitcount_obj = get_object_or_None(HitCount, object_pk=obj.uuid)
        except HitCount.MultipleObjectsReturned:
            # TODO: not sure yet why multiple HitCount could be created.
            hitcount_obj = HitCount.objects.filter(object_pk=obj.uuid)[0]
            logger.error("Multiple object returned in get_view_num: case uuid %s" % obj.uuid)

        if not hitcount_obj:
            return 0
        else:
            return hitcount_obj.hits or 0


class CaseCardSerializer(serializers.ModelSerializer):
    # read-only, so using methodField is sufficient.
    clinic = ClinicInfoBriefSerializer()
    uuid = serializers.ReadOnlyField()

    # this will correctly return full url in endpoints
    # but not when using it standalone in DRF views unless the context is set.
    # bf_img_thumb = serializers.ImageField(max_length=None,
    #                                       use_url=True,
    #                                       required=False)

    af_img_thumb = serializers.ImageField(max_length=None,
                                          use_url=True,
                                          required=False)

    # bf_img_thumb = serializers.SerializerMethodField()

    # author = serializers.SerializerMethodField()
    surgeries = serializers.SerializerMethodField()

    # boolean
    # saved_by_user = serializers.SerializerMethodField(required=False)
    # liked_by_user = serializers.SerializerMethodField(required=False)

    # number
    # like_num = serializers.SerializerMethodField(required=False)
    # view_num = serializers.SerializerMethodField(required=False)

    # 'saved_by_user', 'liked_by_user',
    class Meta:
        model = Case
        fields = ('uuid', 'is_official', 'title', 'af_img_thumb', 'surgeries',
                  'author', 'clinic', 'failed')

    def __init__(self, *args, **kwargs):
        """
        Dynamically change field.

        :param args:
        :param kwargs:
        """
        # is search_view
        self.search_view = kwargs.get("search_view", False)

        # is on saved page
        self.saved_page = kwargs.get("saved_page", False)

        if self.search_view:
            # downstream can't accept this keyword
            kwargs.pop('search_view')

        if self.saved_page:
            # downstream can't accept this keyword
            kwargs.pop('saved_page')

        super(CaseCardSerializer, self).__init__(*args, **kwargs)

        try:
            if self.search_view:
                self.fields['bf_img_thumb'] = serializers.ImageField(max_length=None,
                                                                     use_url=True,
                                                                     required=False)
                self.fields['author'] = serializers.SerializerMethodField()
                # self.fields['logo'] = serializers.SerializerMethodField()
                self.fields['posted'] = serializers.SerializerMethodField(required=False)  # tODO: WIP
                # print("search view-----")

                # if self.saved_page:
                #     self.fields['like_num'] = serializers.SerializerMethodField()
                #     self.fields['view_num'] = serializers.SerializerMethodField()

            else:
                # manage-case or edit mode etc
                self.fields['photo_num'] = serializers.SerializerMethodField()
                self.fields['state'] = serializers.CharField(required=False)
                self.fields['author'] = serializers.SerializerMethodField()  # detail author
                self.fields['posted'] = serializers.CharField(required=False)
                self.fields['author_posted'] = serializers.CharField(required=False)
        except KeyError as e:
            logger.error("[ERROR] CaseCardSerializer: %s" % str(e))

    def get_author(self, obj):
        """
        To serializer EmbeddedModel field from djongo.
        https://github.com/nesdis/djongo/issues/115

        :param obj:
        :return:
        """
        if self.search_view is True:
            return obj.author.scp_username if obj.author.scp else obj.author.name
        else:
            return embedded_model_method(obj, self.Meta.model, 'author',
                                         included_fields=['name', 'scp', 'scp_username'])

    def get_posted(self, obj):
        """
        Return customer-facing posted time (author_posted)
        and fall back to system posted if author_posted does not exist.

        :param obj:
        :return:
        """
        return obj.author_posted or obj.posted

    def get_surgery_meta(self, obj):
        """
        To serializer EmbeddedModel field from djongo.
        :param obj:
        :return:
        """
        return embedded_model_method(obj, self.Meta.model, 'surgery_meta')

    def get_clinic(self, obj):
        """
        To serialize EmbeddedModel from djongo.
        :param obj:
        :return:
        """
        return embedded_model_method(obj, self.Meta.model, 'clinic')

    def get_surgeries(self, obj):
        """
        To serialize ArrayModelField from djongo.
        :param obj:
        :return:
        """
        return embedded_model_method(obj, self.Meta.model, 'surgeries', included_fields=['name'])

    def get_photo_num(self, obj):
        """
        Optional field. If 'show_photo_num' is specified and set to true
        in the request url, it will return the # of photos in the case.

        :param obj:
        :return:
        """
        if not self.context.get('request'):
            return ''

        show_photo_num = self.context.get('request').query_params.get('show_photo_num')
        if show_photo_num and show_photo_num.lower() in ("yes", "true", "t", "1"):
            # get case object
            other_imgs = CaseImages.objects.filter(case_uuid=obj.uuid)
            photo_num = 0
            if obj.bf_img_thumb:
                photo_num += 1

            if obj.af_img_thumb:
                photo_num += 1

            photo_num += len(other_imgs)

            return photo_num
        else:
            return ''

    # def get_saved_by_user(self, obj):
    #     """
    #     Return a boolean flag indicating whether the user
    #     in the request saved the current case.
    #
    #     For unauthorized users, it will always be false.
    #
    #     :param obj: the comment object
    #     :return (boolean):
    #     """
    #     return False
    #
    #     request = self.context.get('request', None)
    #
    #     # for unlogin user
    #     if not request or request.user.is_anonymous:
    #         return False
    #
    #     # it should only have one obj if it's saved
    #     action_objs = obj.action_object_actions.filter(actor_object_id=request.user._id, verb='save')
    #     # logger.info("action_objs in serializer %s" % action_objs)
    #
    #     return False if not action_objs else True

    # def get_liked_by_user(self, obj):
    #     """
    #     Return a boolean flag indicating whether the user
    #     in the request liked the current case.
    #
    #     For unauthorized users, it will always be false.
    #
    #     :param obj: the comment object
    #     :return (boolean):
    #     """
    #     return False
    #
    #     request = self.context.get('request', None)
    #
    #     # for unlogin user
    #     if not request or request.user.is_anonymous:
    #         return False
    #
    #     # it should only have one obj if it's liked
    #     action_objs = obj.action_object_actions.filter(actor_object_id=request.user._id, verb='like')
    #
    #     return False if not action_objs else True

    def get_logo(self, obj):
        """
        Not using
        :param obj:
        :return:
        """
        clinic_obj = get_object_or_None(ClinicProfile, uuid=obj.clinic.uuid)

        if not clinic_obj:
            return ''

        return ClinicLogoSerializer(clinic_obj).data['logo_thumbnail_small']


######################################
#      Detail CRUD Serializers
######################################

NESTED_FIELDS_MODELS = [('clinic', ClinicInfo), ('author', UserInfo),
                        ('surgery_meta', SurgeryMeta)]
NESTED_FIELDS = ['clinic', 'author', 'surgery_meta', 'surgeries']


class CaseImagesSerializer(serializers.ModelSerializer):
    img = serializers.ImageField(max_length=None,
                                 use_url=True,
                                 required=False)

    caption = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CaseImages
        fields = ('img', 'caption')


class CaseImagesCaptionEdit(serializers.Serializer):
    """
    Serializer for editing caption field in CaseImages
    """
    id = serializers.CharField(required=False)
    caption = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField(required=False, min_value=0)


class CaseImagesEditSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField(read_only=True)

    img = serializers.ImageField(max_length=None,
                                 use_url=True,
                                 required=False)

    caption = serializers.CharField(required=False, allow_blank=True)

    order = serializers.IntegerField(required=False, min_value=0)

    def get_id(self, obj):
        return str(obj._id)

    # this won't be called
    # def get_value(self, dictionary):
    #     """
    #     Given the *incoming* primitive data, return the value for this field
    #     that should be validated and transformed to a native value.
    #     """
    #     print('***** dict----------------', dictionary)
    #     if html.is_html_input(dictionary):
    #         # HTML forms will represent empty fields as '', and cannot
    #         # represent None or False values directly.
    #         if self.field_name not in dictionary:
    #             print("***** filed name not in", self.field_name)
    #             if getattr(self.root, 'partial', False):
    #                 return empty
    #             return self.default_empty_html
    #         ret = dictionary[self.field_name]
    #         if ret == '' and self.allow_null:
    #             print("***** 2", self.field_name)
    #             # If the field is blank, and null is a valid value then
    #             # determine if we should use null instead.
    #             return '' if getattr(self, 'allow_blank', False) else None
    #         elif ret == '' and not self.required:
    #             # If the field is blank, and emptiness is valid then
    #             # determine if we should use emptiness instead.
    #             print("***** 3", self.field_name)
    #             return '' if getattr(self, 'allow_blank', False) else empty
    #         return ret
    #     print("***** 4", dictionary.get(self.field_name, empty))
    #     return dictionary.get(self.field_name, empty)


# TODO: WIP. list API should through ES
# TODO: don't know why all the Base64ImageField here don't work
class CaseDetailSerializer(serializers.ModelSerializer):
    uuid = serializers.ReadOnlyField()

    # author = AuthorSerializer(required=False)
    # surgeries = serializers.SerializerMethodField(required=False)  # TODO this works for get only
    # surgeries = SurgeryTagSerializer(many=True) # TODO: this works for post only
    # surgeries = serializers.ListField() # this does not work

    surgery_meta = SurgeryMetaSerializer(required=False)

    # from extra field package. handy. can post base64 directly.
    bf_img_cropped = Base64ImageField(required=False)

    af_img_cropped = Base64ImageField(required=False)

    # other_imgs = CaseImagesSerializer(required=False)   # many = True
    # CaseImagesSerializer2
    other_imgs = CaseImagesSerializer(many=True, required=False)
    # other_imgs = serializers.ListField(child=serializers.CharField(), required=False)
    # other_imgs = serializers.ListField(child=serializers.ImageField(), required=False)

    # anesthesia = serializers.CharField(source='get_anesthesia_display', required=False)

    scp_user_pic = serializers.ImageField(max_length=None,
                                          use_url=True,
                                          required=False)

    side_effects = serializers.ListField(required=False)

    pain_points = serializers.ListField(required=False)

    positive_exp = serializers.ListField(required=False)

    comment_num = serializers.SerializerMethodField(required=False)
    comments = serializers.SerializerMethodField(required=False)

    posted = serializers.SerializerMethodField(required=False)  # tODO: WIP

    class Meta:
        model = Case
        # fields = "__all__"
        fields = ('uuid', 'is_official', 'title', 'bf_img_cropped', 'bf_cap',
                  'af_img_cropped', 'af_cap', 'surgeries', 'author', 'state', 'other_imgs',
                  'body', 'surgery_meta', 'rating', 'bf_img_cropped', 'posted',
                  'recovery_time', 'anesthesia', 'scp_user_pic', 'positive_exp', 'side_effects', 'pain_points',
                  'ori_url', 'comment_num', 'comments', 'failed')

    # def _force_get_value(self, dictionary):
    #     print("!!!!!!!!! set value")
    #     return dictionary.get('other_imgs', empty)

    @staticmethod
    def _force_get_value_factory(field_name):
        def get_value(dictionary):
            # print("!!!!!!!!! set value", field_name, dictionary)
            return dictionary.get(field_name, empty)

        return get_value

    def __init__(self, *args, **kwargs):
        """
        Dynamically change field.
        https://stackoverflow.com/questions/38316321/
        change-a-field-in-a-django-rest-framework-modelserializer-based-on-the-request-t

        :param args:
        :param kwargs:
        """
        super(CaseDetailSerializer, self).__init__(*args, **kwargs)

        edit_param = self.context.get('request').query_params.get('edit')
        self.edit_mode = True if (edit_param and edit_param.lower() in ("yes", "true", "t", "1")) else False

        # self.fields['other_imgs'].get_value = self._force_get_value
        self.fields['other_imgs'].get_value = self._force_get_value_factory(self.fields['other_imgs'].field_name)

        # if 'request' in self.context:
        #    print("======data", self.context['request'].data)

        try:
            if self.context['request'].method in ['POST', 'PUT', 'PATCH']:
                # need to set required=False for post.
                self.fields['bf_img'] = serializers.ImageField(max_length=None,
                                                               use_url=True,
                                                               required=False)

                self.fields['af_img'] = serializers.ImageField(max_length=None,
                                                               use_url=True,
                                                               required=False)

                self.fields['surgeries'] = SurgeryTagSerializer(many=True)
                self.fields['scp_user_pic'] = serializers.ImageField(max_length=None,
                                                                     use_url=True,
                                                                     required=False)
                self.fields['author'] = AuthorSerializer(required=False)
                self.fields['clinic'] = ClinicInfoSerializer(required=False)
                # if self.context['request'].method != 'POST':
                # self.fields['other_imgs'] = CaseImagesSerializer(many=True, required=False)  # many=True
                # self.fields['other_imgs'] = serializers.ListField(required=False)
                if self.context['request'].method != 'POST':
                    # PUT or PATCH
                    self.fields['img_to_delete'] = serializers.ListField(required=False)
                    # for editing caption
                    self.fields['captions_edit'] = CaseImagesCaptionEdit(many=True, required=False)

                # can happen in both POST and PUT/PATCH.
                # this is for newly created CaseImages
                self.fields['captions'] = serializers.CharField(required=False)
                self.fields['orders'] = serializers.CharField(required=False)
            else:  # GET
                self.fields['surgeries'] = serializers.SerializerMethodField()
                self.fields['other_imgs'] = serializers.SerializerMethodField()
                self.fields['author'] = serializers.SerializerMethodField()
                self.fields['clinic'] = ClinicInfoURLSerializer()
                if self.edit_mode:
                    # return img url if it's edit mode
                    self.fields['scp_user_pic'] = serializers.ImageField(max_length=None,
                                                                         use_url=True,
                                                                         required=False)
                    self.fields['bf_img'] = serializers.ImageField(max_length=None,
                                                                   use_url=True,
                                                                   required=False)

                    self.fields['af_img'] = serializers.ImageField(max_length=None,
                                                                   use_url=True,
                                                                   required=False)
                else:
                    # return thumbnail base64 if it's read-only GET
                    self.fields['scp_user_pic'] = serializers.SerializerMethodField(required=False)
        except KeyError:
            pass

    def create(self, validated_data):
        """
        Create a case instance.

        :param validated_data:
        :return:
        """
        # print("validated data, create", validated_data)
        #
        # if 'other_imgs' in validated_data:
        #     print("oooo created", validated_data['other_imgs'], type(validated_data['other_imgs'][0]))
        #     serializer = CaseImagesSerializer(validated_data['other_imgs'], many=True)
        #     print("??? created", serializer.data)

        # TODO: hard-coded pop
        # TODO: key error
        author = {} if 'author' not in validated_data else validated_data.pop('author')
        clinic = {} if 'clinic' not in validated_data else validated_data.pop('clinic')
        surgery_meta = {} if 'surgery_meta' not in validated_data else validated_data.pop('surgery_meta')
        surgeries = [] if 'surgeries' not in validated_data else validated_data.pop('surgeries')
        # positive_exp = [] if 'positive_exp' not in validated_data else validated_data.pop('positive_exp')

        # print("positive_exp", positive_exp)

        surgeries_objs = []
        for surgery in surgeries:
            surgery_tag = SurgeryTag(name=surgery.get('name', ''), mat=surgery.get('mat', ''))
            surgeries_objs.append(surgery_tag)

        request = self.context.get('request', None)
        request_user = None if not request else request.user

        # can't directly use create here as I need to attach an unknown field _request_user
        # for the sake of updating author_posted signal
        # case_obj = Case.objects.create
        case_obj = Case(**validated_data,
                        author=UserInfo(name=author.get('name', ''),
                                        uuid=author.get('uuid', ''),
                                        scp_username=author.get('scp_username', '')),
                        clinic=ClinicInfo(display_name=clinic.get('display_name', ''),
                                          branch_name=clinic.get('branch_name', ''),
                                          doctor_name=clinic.get('doctor_name', '')),
                        surgery_meta=SurgeryMeta(year=int(surgery_meta.get('year', 0)) or None,
                                                 # None not ''
                                                 month=int(surgery_meta.get('month', 0)) or None,
                                                 min_price=int(surgery_meta.get('min_price', 0)) or None,
                                                 max_price=int(
                                                     surgery_meta.get('max_price', 0)) or None),
                        surgeries=surgeries_objs)

        case_obj._request_user = request_user
        case_obj.save()
        # if author:
        #     UserInfo.objects.create(**author)
        return case_obj

    def update(self, instance, validated_data):
        """
        Update a case instance.

        :param instance:
        :param validated_data:
        :return:
        """
        # TODO: need more test
        # TODO: remove prints and change them to loggings.

        # TODO: WIP
        # print("validate, update", validated_data, instance.uuid)

        # when creating new other imgs
        captions = []
        if 'captions' in validated_data:
            try:
                captions = ast.literal_eval(validated_data['captions'])
                logger.info("get captions: %s" % captions)
            except SyntaxError as e:
                logger.error('update case captions error %s' % str(e))

        orders = []
        if 'orders' in validated_data:
            try:
                orders = ast.literal_eval(validated_data['orders'])
                logger.info("get orders: %s" % orders)
            except SyntaxError as e:
                logger.error('update case captions error %s' % str(e))

        # when editing captions of existing other imgs
        if validated_data.get('captions_edit', []):
            for item in validated_data.get('captions_edit', []):
                if item.get('id', ''):
                    img_instance = get_object_or_None(CaseImages,
                                                      _id=ObjectId(item['id']),
                                                      case_uuid=instance.uuid)
                    if img_instance:
                        # update caption
                        img_instance.caption = item.get('caption', '')
                        # update order
                        order = item.get('order', '')
                        if order is not None and order != '':
                            # print("!!!!update order to ", order)
                            img_instance.order = order

                        img_instance.save()
                    else:
                        logger.error('No case img with id %s' % item['id'])

        if 'other_imgs' in validated_data:
            # print("oooo", validated_data['other_imgs'])
            other_imgs = validated_data['other_imgs']
            if len(captions) != len(other_imgs):
                # since we match caption and other_imgs based on the sequence,
                # they must have the same lengths. If not, we'll drop them.
                logger.warning("caption len not matched. Got %s captions but %s other imgs"
                               % (len(captions), len(other_imgs)))
                captions = [''] * len(other_imgs)

            # check order length
            # TODO: this logic needs to be improved.
            if len(orders) != len(other_imgs):
                # since we match caption and other_imgs based on the sequence,
                # they must have the same lengths. If not, we'll drop them.
                logger.warning("orders len not matched. Got %s orders but %s other imgs"
                               % (len(orders), len(other_imgs)))
                orders = [None] * len(other_imgs)

            for i, item in enumerate(other_imgs):
                new_instance = CaseImages(img=item.get('img', ''),
                                          caption=captions[i],
                                          order=orders[i],
                                          case_uuid=instance.uuid)
                new_instance.save()

            # serializer = CaseImagesSerializer(validated_data['other_imgs'], many=True)
            # print("???", serializer.data)

        # for deleting CaseImg
        if 'img_to_delete' in validated_data:
            # print("img to delete", validated_data['img_to_delete'])

            # TODO: add some try, except. right now is pretty fragile.
            for item in validated_data['img_to_delete']:
                # if item == 'af_img' or item == 'bf_img':
                #     # imagekit processed field
                #     try:
                #         # delete cache file first
                #         # this is because imagekit doesn't have a simple
                #         # thumb.delete() function ....
                #         field = getattr(instance, '%s_thumb' % item)
                #         file = field.file
                #         path_name = field.path
                #         cache_backend = field.cachefile_backend
                #         cache_backend.cache.delete(cache_backend.get_key(file))
                #         field.storage.delete(file)
                #         logger.info("[case signal %s] clear out cache %s " % (instance.uuid, path_name))
                #     # AttributeError
                #     except Exception as e:
                #         logger.error("[case signal %s Error deleting cache]: %s" % (instance.uuid, str(e)))
                #
                #     try:
                #         # then, delete the original imgs
                #         getattr(instance, item).delete()
                #         getattr(instance, '%s_cropped' % item).delete()
                #     except Exception as e:
                #         logger.error("[case signal %s Error deleting ori imgs]: %s" % (instance.uuid, str(e)))
                if item == 'bf_img':
                    # imagekit processed field
                    try:
                        # delete cache file first
                        # this is because imagekit doesn't have a simple
                        # thumb.delete() function ....
                        field = instance.bf_img_thumb
                        file = field.file
                        path_name = field.path
                        cache_backend = field.cachefile_backend
                        cache_backend.cache.delete(cache_backend.get_key(file))
                        field.storage.delete(file)
                        logger.info("[case signal %s] clear out cache %s " % (instance.uuid, path_name))
                    # AttributeError
                    except Exception as e:
                        logger.error("[case signal %s Error deleting cache]: %s" % (instance.uuid, str(e)))

                    instance.bf_img.delete()
                    instance.bf_img_cropped.delete()
                elif item == 'af_img':
                    # imagekit processed field
                    try:
                        # delete cache file first
                        field = instance.af_img_thumb
                        file = field.file
                        path_name = field.path
                        cache_backend = field.cachefile_backend
                        cache_backend.cache.delete(cache_backend.get_key(file))
                        field.storage.delete(file)
                        logger.info("[case signal %s] clear out cache %s " % (instance.uuid, path_name))
                    # AttributeError
                    except Exception as e:
                        logger.error("[case signal %s Error deleting cache]: %s" % (instance.uuid, str(e)))

                    instance.af_img.delete()
                    instance.af_img_cropped.delete()
                else:
                    try:
                        img_instance = get_object_or_None(CaseImages,
                                                          _id=ObjectId(item),
                                                          case_uuid=instance.uuid)
                        if img_instance:
                            # print("delete CaseImg", img_instance) # TODO: need further check
                            img_instance.delete()
                    except Exception as e:
                        logger.error('Cannot delete CaseImages with id %s' % item)

        # ArrayModelField
        if 'surgeries' in validated_data:
            surgeries_objs = []
            for surgery in validated_data['surgeries'] or []:
                surgery_tag = SurgeryTag(name=surgery.get('name', ''), mat=surgery.get('mat', ''))
                surgeries_objs.append(surgery_tag)
            instance.surgeries = surgeries_objs

        # EmbeddedModelField
        for (nested_field, Current_model) in NESTED_FIELDS_MODELS:
            # print('---', nested_field, Current_model)
            if nested_field in validated_data:
                new_data = validated_data[nested_field]
                ori_obj = getattr(instance, nested_field) or Current_model()
                # for all nested fields under this field
                for field in Current_model._meta.get_fields():  # TODO: has bug
                    field_name = field.name
                    if field_name in new_data:
                        setattr(ori_obj, field_name, new_data.get(field_name, ''))
                        # clinic_obj._meta.get_field(field_name) = new_data[field_name]
                # print("obj", ori_obj, ori_obj.doctor_name)
                setattr(instance, nested_field, ori_obj)
                # instance.clinic = ori_obj

        # others
        for field in Case._meta.get_fields():
            field_name = field.name
            if field_name not in NESTED_FIELDS:
                # print("check field", field_name)
                if field_name in validated_data:
                    setattr(instance, field_name, validated_data[field_name])
                # instance.bf_img = validated_data.get('clinic', instance.email)
        # instance.clinic = validated_data.get('clinic', instance.email)
        # instance.content = validated_data.get('content', instance.content)
        # instance.created = validated_data.get('created', instance.created)

        request = self.context.get('request', None)
        if request:
            instance._request_user = request.user

        instance.save()
        return instance

    def get_author(self, obj):
        """
        To serializer EmbeddedModel field from djongo.
        https://github.com/nesdis/djongo/issues/115

        :param obj:
        :return:
        """
        if not self.edit_mode:
            # public search view
            return obj.author.scp_username if obj.author.scp else obj.author.name
        else:
            return embedded_model_method(obj, self.Meta.model, 'author',
                                         included_fields=['name', 'scp', 'scp_username'])

    def get_posted(self, obj):
        """
        Return customer-facing posted time (author_posted)
        and fall back to system posted if author_posted does not exist.

        :param obj:
        :return:
        """
        return obj.author_posted or obj.posted

    def get_surgery_meta(self, obj):
        """
        To serialize EmbeddedModel from djongo.
        :param obj:
        :return:
        """
        return embedded_model_method(obj, self.Meta.model, 'surgery_meta')

    def get_clinic(self, obj):
        """
        To serialize EmbeddedModel from djongo.
        :param obj:
        :return:
        """
        return embedded_model_method(obj, self.Meta.model, 'clinic')

    def get_surgeries(self, obj):
        """
        To serialize ArrayModelField from djongo.
        :param obj:
        :return:
        """
        return embedded_model_method(obj, self.Meta.model, 'surgeries')

    # TODO: tmp try
    def get_other_imgs(self, obj):
        objs = CaseImages.objects.filter(case_uuid=obj.uuid)
        # this will sort objs by 'order' field None to the end
        objsSsorted = sorted(objs, key=lambda x: (x.order is None, x.order))

        objsToReturn = objs
        # if all other images has and non-none order,
        # return the imgs based on the order field.
        if objsSsorted and objsSsorted[-1].order is not None:
            objsToReturn = objsSsorted
            # print("used sorted.")

        if self.edit_mode:
            # decide whether to sort
            serializer = CaseImagesEditSerializer(objsToReturn,
                                                  many=True,
                                                  context={'request': self.context['request']})
        else:
            serializer = CaseImagesSerializer(objsToReturn,
                                              many=True,
                                              context={'request': self.context['request']})

        # [item.get('img', '') for item in serializer.data]
        return [] if not objs else serializer.data

    def get_scp_user_pic(self, obj):
        # TODO: add in user profile pic
        if obj.scp_user_pic_thumb:
            return image_as_base64(obj.scp_user_pic_thumb.url)
        return ''

    def get_comments(self, obj):
        """
        Get a list of comments of a given post
        :param obj:
        :return:
        """
        # TODO: fix this!!
        # only get first-level comments, which have null or empty reply_to_id
        objs = Comment.objects.filter(Q(reply_to_id='') | Q(reply_to_id__isnull=True)) \
            .filter(case_id=obj.uuid).order_by('-posted')
        objs = objs[:min(len(objs), COMMENT_PAGE_SIZE)]
        # TODO: could remove the case_id in the serializer
        serializer = CommentSerializer(objs, many=True, context={'request': self.context['request']})

        return [] if not objs else serializer.data

    def get_comment_num(self, obj):
        """
        Number of comments

        :param obj:
        :return:
        """
        objs = Comment.objects.filter(Q(reply_to_id='') | Q(reply_to_id__isnull=True)) \
            .filter(case_id=obj.uuid)
        return len(objs)
