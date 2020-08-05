"""
Fields Utilities

"""

from time import time
from random import SystemRandom
import os
import base64
import hashlib

from django.conf import settings


# an arbitrary start time for make_id()
_START_TIME = 1529056153044
# _START_TIME = int(time() * 1000)


def make_id():
    """
    Used as BigIntegerField in model that
    contains unique id with the purpose of not
    revealing the real pk.

    :return(long): a unique id.
    """
    t = int(time() * 1000) - _START_TIME
    u = SystemRandom().getrandbits(15)
    uuid = (t << 15) | u

    return uuid


def reverse_id(uuid):
    """
    The reversed method for make_id()
    :param uuid:
    :return:
    """
    t = uuid >> 15
    return t + _START_TIME


def image_as_base64(image_file):
    """
    Change File object to base64 string.
    :param `image_file` for the complete path of image.
    :param `format` is format for image, eg: `png` or `jpg`.
    """
    img_format = ''
    if image_file:
        img_format = image_file.split('.')[-1]

    if image_file.startswith('/'):
        image_file = image_file[1:]

    # TODO: this might not working for prod static file settings
    img_full_path = os.path.join(settings.TOP_DIR, image_file)

    if not img_format or not os.path.isfile(img_full_path):
        return ''

    encoded_string = ''
    with open(img_full_path, 'rb') as img_f:
        # need to encode, otherwise will return bytes
        encoded_string = base64.b64encode(img_f.read()).decode("utf-8")
    return 'data:image/%s;base64,%s' % (img_format, encoded_string)


def hash_text(s):
    """
    SHA256 hash or text to 8 digits.

    :param s: text to hash
    :return:
    """

    return int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16) % 10**8
