from rest_framework import serializers


class AuthorSerializer(serializers.Serializer):
    """
    Serializer for author field.
    """
    uuid = serializers.CharField()
    name = serializers.CharField()
    scp = serializers.BooleanField(required=False)
    scp_username = serializers.CharField(required=False, allow_blank=True)


# TODO: I forgot what this is for
class PartialAuthorSerializer(serializers.Serializer):
    name = serializers.CharField()
    scp_username = serializers.CharField(required=False, allow_blank=True)
