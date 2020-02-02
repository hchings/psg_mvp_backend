"""
REST Framework Serializers for Case app.

"""

from rest_framework import serializers, exceptions
from drf_extra_fields.fields import Base64ImageField

from backend.shared.fields import embedded_model_method
from .models import Case, CaseImages, UserInfo, ClinicInfo, SurgeryMeta, SurgeryTag


#########################################################
#    Field Serializers for djongo's EmbeddedModelField
#    This will handle post?
#########################################################

class AuthorSerializer(serializers.Serializer):
    """
    Serializer for author field.
    """
    uuid = serializers.CharField()
    name = serializers.CharField()


class ClinicInfoSerializer(serializers.Serializer):
    """
    Serializer for clinic field.
    """
    display_name = serializers.CharField()
    branch_name = serializers.CharField(required=False, allow_blank=True)
    doctor_name = serializers.CharField(required=False, allow_blank=True)
    place_id = serializers.ReadOnlyField()
    uuid = serializers.ReadOnlyField()


class SurgeryMetaSerializer(serializers.Serializer):
    """
    Serializer for surgery_meta field.
    """
    year = serializers.IntegerField(required=False, min_value=0)
    month = serializers.IntegerField(required=False, min_value=1)
    dateString = serializers.CharField(required=False, allow_blank=True)


class SurgeryTagSerializer(serializers.Serializer):
    """
    Serializer for surgeries field.
    """
    name = serializers.CharField(required=False, allow_blank=True)
    mat = serializers.CharField(required=False, allow_blank=True)


######################################
#     Card-view (brief) Serializers
######################################


class CaseCardSerializer(serializers.ModelSerializer):
    # read-only, so using methodField is sufficient.
    clinic = serializers.SerializerMethodField()
    uuid = serializers.ReadOnlyField()

    # this will correctly return full url in endpoints
    # but not when using it standalone in DRF views unless the context is set.
    bf_img_thumb = serializers.ImageField(max_length=None,
                                          use_url=True,
                                          required=False)

    af_img_thumb = serializers.ImageField(max_length=None,
                                          use_url=True,
                                          required=False)

    # bf_img_thumb = serializers.SerializerMethodField()

    author = serializers.SerializerMethodField()
    surgeries = serializers.SerializerMethodField()
    surgery_meta = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = ('uuid', 'is_official', 'pbm', 'title', 'bf_img_thumb', 'af_img_thumb', 'surgeries', 'posted',
                  'author', 'state', 'clinic', 'view_num', 'surgery_meta')

    def get_author(self, obj):
        """
        To serializer EmbeddedModel field from djongo.
        https://github.com/nesdis/djongo/issues/115

        :param obj:
        :return:
        """
        return embedded_model_method(obj, self.Meta.model, 'author')

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
        return embedded_model_method(obj, self.Meta.model, 'surgeries')


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


# TODO: WIP. list API should through ES
class CaseDetailSerializer(serializers.ModelSerializer):
    uuid = serializers.ReadOnlyField()
    clinic = ClinicInfoSerializer(required=False)
    author = AuthorSerializer(required=False)
    # surgeries = serializers.SerializerMethodField(required=False)  # TODO this works for get only
    # surgeries = SurgeryTagSerializer(many=True) # TODO: this works for post only
    # surgeries = serializers.ListField() # this does not work

    surgery_meta = SurgeryMetaSerializer(required=False)

    # need to set required=False for post.
    bf_img = serializers.ImageField(max_length=None,
                                    use_url=True,
                                    required=False)
    # from extra field package. handy. can post base64 directly.
    bf_img_cropped = Base64ImageField(required=False)

    af_img = serializers.ImageField(max_length=None,
                                    use_url=True,
                                    required=False)
    af_img_cropped = Base64ImageField(required=False)

    other_imgs = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Case
        # fields = "__all__"
        fields = ('uuid', 'is_official', 'pbm', 'title', 'bf_img', 'bf_img_cropped', 'bf_cap',
                  'af_img', 'af_img_cropped', 'af_cap', 'other_imgs', 'surgeries', 'author', 'state',
                  'clinic', 'view_num', 'body', 'surgery_meta', 'rating', 'bf_img_cropped')

    def __init__(self, *args, **kwargs):
        """
        Dynamically change field.
        https://stackoverflow.com/questions/38316321/
        change-a-field-in-a-django-rest-framework-modelserializer-based-on-the-request-t

        :param args:
        :param kwargs:
        """
        super(CaseDetailSerializer, self).__init__(*args, **kwargs)

        try:
            if self.context['request'].method in ['POST', 'PUT', 'PATCH']:
                self.fields['surgeries'] = SurgeryTagSerializer(many=True)
            else:
                self.fields['surgeries'] = serializers.SerializerMethodField()
        except KeyError:
            pass

    def create(self, validated_data):
        """
        Create a case instance.

        :param validated_data:
        :return:
        """
        # print("validated data", validated_data)

        # TODO: hard-coded pop
        # TODO: key error
        author = {} if 'author' not in validated_data else validated_data.pop('author')
        clinic = {} if 'clinic' not in validated_data else validated_data.pop('clinic')
        surgery_meta = {} if 'surgery_meta' not in validated_data else validated_data.pop('surgery_meta')
        surgeries = [] if 'surgeries' not in validated_data else validated_data.pop('surgeries')

        surgeries_objs = []
        for surgery in surgeries:
            surgery_tag = SurgeryTag(name=surgery.get('name', ''), mat=surgery.get('mat', ''))
            surgeries_objs.append(surgery_tag)

        # validated_data['author'] = UserInfo.objects.create({'name': 'gth', 'uuid': 'wtf'})
        case_obj = Case.objects.create(**validated_data,
                                       author=UserInfo(name=author.get('name', ''),
                                                       uuid=author.get('uuid', '')),
                                       clinic=ClinicInfo(display_name=clinic.get('display_name', ''),
                                                         branch_name=clinic.get('branch_name', ''),
                                                         doctor_name=clinic.get('doctor_name', '')),
                                       surgery_meta=SurgeryMeta(dateString=surgery_meta.get('dateString', '')),
                                       surgeries=surgeries_objs)
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

        # ArrayModelField
        if 'surgeries' in validated_data:
            surgeries_objs = []
            for surgery in validated_data['surgeries'] or []:
                surgery_tag = SurgeryTag(name=surgery.get('name', ''), mat=surgery.get('mat', ''))
                surgeries_objs.append(surgery_tag)
            instance.surgeries = surgeries_objs

        # EmbeddedModelField
        for (nested_field, Current_model) in NESTED_FIELDS_MODELS:
            print('---', nested_field, Current_model)
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
                print("check field", field_name)
                if field_name in validated_data:
                    setattr(instance, field_name, validated_data[field_name])
                # instance.bf_img = validated_data.get('clinic', instance.email)
        # instance.clinic = validated_data.get('clinic', instance.email)
        # instance.content = validated_data.get('content', instance.content)
        # instance.created = validated_data.get('created', instance.created)
        instance.save()
        return instance

    def get_author(self, obj):
        """
        To serialize EmbeddedModel from djongo.
        :param obj:
        :return:
        """
        return embedded_model_method(obj, self.Meta.model, 'author')

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
        serializer = CaseImagesSerializer(objs, many=True, context={'request': self.context['request']})

        # [item.get('img', '') for item in serializer.data]
        return [] if not objs else serializer.data
