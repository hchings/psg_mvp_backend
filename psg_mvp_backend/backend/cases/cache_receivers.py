"""
Receivers to warm up cache.

"""

from multiprocessing import Process
import coloredlogs, logging

from django.dispatch import receiver
from django.http import HttpRequest
from django.contrib.sessions.backends.db import SessionStore

from .cache_signals import warmup_cache
from .views import CaseSearchView, CaseDetailView


# Create a logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


def _warmup_default_search():
    request = HttpRequest()

    # fill in request
    request.method = 'POST'
    request.data = {}  # default search

    # call case search view
    try:
        res = CaseSearchView.as_view()(request).data
        results = res.get('results', [])
        # print(res)

        logger.info("Warming up cache....%s records got on landing page" % len(results))

        case_uuids = [case['uuid'] for case in results if 'uuid' in case]
        # print(case_uuids)

        # ----- warm up case detail end points -----
        # create a new session
        # case detail page has hitcount, thus it needs some session data..
        s = SessionStore()
        s.create()

        # create a new request
        request = HttpRequest()
        request.method = 'GET'
        request.META = {}
        request.META['SERVER_NAME'] = 'localhost'
        request.META['SERVER_PORT'] = '8000'
        request.session = s

        # request.session.create()

        for i, uuid in enumerate(case_uuids):
            res = CaseDetailView.as_view()(request, uuid=uuid)
            if int(res.status_code) != 200:
                logger.error("%s got %s" % (i, res.status_code))

        logger.info("cache warm up finished.")

        del request
        del s
        # print(case_uuids)
    except Exception as e:
        logger.error("[Error] cache warmup failed: %s"  % str(e))



@receiver(warmup_cache)
def cache_warmup(sender, **kwargs):
    """
    Warm up cache.
        1) default search
        2) all case details

    :param sender:
    :param kwargs:
    :return:
    """
    # TODO: WIP
    p = Process(target=_warmup_default_search, args=())
    p.start()
    p.join()

    # _warmup_default_search()
