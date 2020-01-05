"""
DRF Serializers for Comments app.

"""

from rest_framework import serializers, exceptions

from cases.models import UserInfo
from cases.serializers import AuthorSerializer
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    # author = serializers.SerializerMethodField()
    author = AuthorSerializer()

    class Meta:
        model = Comment
        fields = ('case_id', 'posted', 'author', 'text')

    def create(self, validated_data):
        """
        Need to pop any embeddedmodel field of djongo and create the abstract
        item by ourselves.
        More info: https://github.com/nesdis/djongo/issues/238

        :param validated_data:
        :return:
        """
        # print("validated data", validated_data)
        author = validated_data.pop('author')
        case_obj = Comment.objects.create(**validated_data,
                                          author=UserInfo(name=author.get('name', ''),
                                                          uuid=author.get('uuid', '')))
        return case_obj

    # def get_author(self, obj):
    #     return embedded_model_method(obj, self.Meta.model, 'author')
