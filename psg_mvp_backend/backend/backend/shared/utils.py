"""
Fields Utilities

"""

from time import time
from random import SystemRandom
import os, json
import base64
import hashlib
from random import randint

from django.conf import settings
from django.core.cache import cache

from backend.settings import FIXTURE_ROOT

# an arbitrary start time for make_id()
_START_TIME = 1529056153044
# _START_TIME = int(time() * 1000)

# store a set of cache keys
# as Memcached does not support wildcard nor loop through all keys
CASE_SEARCH_CACHE_KEYS = set()

# for catelog and tags
CATALOG_FILE = os.path.join(FIXTURE_ROOT, 'catalog.json')
surgery_mat_list = []
sub_cate = {}
sub_cate_to_cate = {} # sub category to 1-st layer category


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


def _prep_catalog():
    """
    Prep for surgery stuff.
    Only read file for once on initial call.
    Values will be cached.

    :return:
    """
    # read in json catalog only once
    if not surgery_mat_list or not sub_cate_to_cate:
        catalog_dict = {}
        with open(CATALOG_FILE) as json_file:
            catalog_dict = json.load(json_file)

        for item in catalog_dict.get('catalog_items', []):
            for subcat in item.get('subcategory', []):
                name = subcat.get('name', '')
                if name:
                    # pop key if exist
                    subcat.pop('syn', None)
                    surgery_mat_list.append(subcat)
                    sub_cate_to_cate[name] = item['category']

        # print("sub_cate to cate", sub_cate_to_cate)
    return surgery_mat_list, sub_cate_to_cate


def _prep_subcate():
    """
    Prep for <surgery cartegory>: [list of surgery subcate].

    :return(dict): <surgery cartegory>: [list of surgery subcate].
    """
    if not sub_cate or not sub_cate_to_cate:
        catalog_dict = {}
        with open(CATALOG_FILE) as json_file:
            catalog_dict = json.load(json_file)

        for item in catalog_dict.get('catalog_items', []):
            category = item.get('category', '')
            if category and item.get('subcategory', []):
                # print("dsds", item['subcategory'])
                # sub_cate[category] = [sub['name'] for sub in item['subcategory'] if sub.get('name', '')]

                sub_cate[category] = []
                for sub in item['subcategory']:
                    if sub.get('name', ''):
                        sub_cate[category].append(sub['name'])
                        sub_cate_to_cate[sub['name']] = category


    # print("subcate", sub_cate)
    print("generated sub cate to cate.")
    return sub_cate, sub_cate_to_cate


def random_with_n_digits(n):
    """
    Gen random numerical code in n digits.
    This is primarily used for otp.

    :param n:
    :return:
    """
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

#######################
#         CACHE
#######################

def invalidate_cached_data(cache_key, case_search_wildcard=False):
    """
    Invalid cache data by cache key.

    :param(str) cache_key: now defined in each view.py
    :param(boolean) case_search_wildcard: When set to true, will wipe out any keys
                                          stored in CASE_SEARCH_CACHE_KEYS

    :return:
    """
    if case_search_wildcard:
        global CASE_SEARCH_CACHE_KEYS
        for key in CASE_SEARCH_CACHE_KEYS:
            # print("=====invalid search cache key:", key)
            cache.delete(key)

        # wipe out the whole CASE_SEARCH_CACHE_KEYS
        CASE_SEARCH_CACHE_KEYS = set()
    else:
        # print("=====invalid cache key:", cache_key)
        cache.delete(cache_key)


def add_to_cache(cache_key, data, store_key=True):
    """
    Add data to a cache key.

    :param cache_key:
    :param data:
    :param store_key: store key to CASE_SEARCH_CACHE_KEYS
    :return:
    """
    cache.set(cache_key, data)
    if store_key:
        CASE_SEARCH_CACHE_KEYS.add(cache_key)
