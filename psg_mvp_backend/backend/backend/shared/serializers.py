from rest_framework import serializers


class AuthorSerializer(serializers.Serializer):
    """
    Serializer for author field.
    """
    uuid = serializers.CharField()
    name = serializers.CharField()


class PartialAuthorSerializer(serializers.Serializer):
    name = serializers.CharField()
