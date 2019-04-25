"""
Fields Utilities

"""

from time import time
from random import SystemRandom


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
