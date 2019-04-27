"""
Custom fields for DRF.

"""

from base64 import b64encode

from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for serializing file stored in ImageField
    into a base64 string.

    Note that DRF field has a built-in parameter argument "source",
    which you can use to specify the source field.

    Does not support writing img as base64. For that use, see:
    https://github.com/tomchristie/django-rest-framework/pull/1268

    """
    def to_representation(self, file):
        """

        :param file: the image file
        :return:
        """
        if not file:
            # TODO: change it to serve default img
            return ''
        with open(file.path, 'rb') as f:
            # now it's a byte str, need to decode to str
            encoded_str = b64encode(f.read()).decode("utf-8")

        extension = file.name.split(".")[-1]
        return 'data:image/%s;base64,%s' % (extension, encoded_str)

    # def to_internal_value(self, data):
    #     from django.core.files.base import ContentFile
    #     import base64
    #     import six
    #     import uuid
    #
    #     # Check if this is a base64 string
    #     if isinstance(data, six.string_types):
    #         # Check if the base64 string is in the "data:" format
    #         if 'data:' in data and ';base64,' in data:
    #             # Break out the header from the base64 content
    #             header, data = data.split(';base64,')
    #
    #         # Try to decode the file. Return validation error if it fails.
    #         try:
    #             decoded_file = base64.b64decode(data)
    #         except TypeError:
    #             self.fail('invalid_image')
    #
    #         # Generate file name:
    #         file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
    #         # Get the file name extension:
    #         file_extension = self.get_file_extension(file_name, decoded_file)
    #
    #         complete_file_name = "%s.%s" % (file_name, file_extension, )
    #
    #         data = ContentFile(decoded_file, name=complete_file_name)
    #
    #     return super(Base64ImageField, self).to_internal_value(data)

    # def get_file_extension(self, file_name, decoded_file):
    #     import imghdr
    #
    #     extension = imghdr.what(file_name, decoded_file)
    #     extension = "jpg" if extension == "jpeg" else extension
    #
    #     return extension
