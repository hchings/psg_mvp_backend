"""
Command to clean up existing cases in database when new fields created.
Use w/ cautious.

To run:
    python manage.py shuffle_cases

"""
import requests
import itertools
import random
import coloredlogs, logging
from algoliasearch.search_client import SearchClient

from django.core.management.base import BaseCommand, CommandError

from backend.settings import ALGOLIA_APP_ID, ALGOLIA_ANALYTIC_KEY, \
    ALGOLIA_CASE_INDEX, ALGOLIA_SECRET
from backend.shared.tasks import update_algolia_records
from cases.models import Case
from cases.serializers import CaseStatsSerializer

# Create a logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

UNIT = 16
GOOD_POST_RATIO = 0.4
PAGES = 4


class Command(BaseCommand):
    """
    Set rank for a subset of cases in Algolia."

    """
    help = "Set rank for a subset of cases in Algolia."

    headers = {
        'X-Algolia-API-Key': ALGOLIA_ANALYTIC_KEY,
        'X-Algolia-Application-Id': ALGOLIA_APP_ID,
    }

    params = {'index': ALGOLIA_CASE_INDEX}

    def handle(self, *args, **options):
        # ===== Step 1 - get a blend of recent and good cases =====
        num_all_cases = UNIT * PAGES
        num_good_cases = int(num_all_cases * GOOD_POST_RATIO)

        recent_cases = Case.objects.filter(state='published').order_by('-posted')[:(num_all_cases - num_good_cases)]
        dedup_uuid = set([case.uuid for case in recent_cases])
        logger.info("Get %s recent cases" % len(recent_cases))

        # get top search results, to determine what good cases to surface
        response = requests.get('https://analytics.algolia.com/2/searches',
                                headers=self.headers,
                                params=self.params)

        response = response.json().get("searches", [])
        good_cases = []
        good_cases_dict = {}
        cnt = 0
        for item in response:
            search_term = item.get("search", "")
            hit_counts = item.get('nbHits', 0)
            if search_term and hit_counts:
                _cases = Case.objects.filter(state='published',
                                             surgeries={'name': search_term})
                if _cases:
                    for case in _cases:
                        if case.uuid not in dedup_uuid:
                            dedup_uuid.add(case.uuid)
                            good_cases.append(case)
                            good_cases_dict[case.uuid] = case
                    logger.info("Top %s search term: %s (#hit_counts=%s, #cases=%s)"
                                % (cnt, search_term, hit_counts, len(_cases)))
                    cnt += 1

            if cnt > 4:
                break

        logger.info("Get %s good cases" % len(good_cases))

        # get view counts
        serializer = CaseStatsSerializer(good_cases, many=True)
        view_dict = {item['uuid']: item['view_num'] for item in serializer.data}
        view_dict = dict(sorted(view_dict.items(), key=lambda x: x[1], reverse=True))
        view_dict = dict(itertools.islice(view_dict.items(), num_good_cases))

        final_cases = list(recent_cases) + [good_cases_dict[uuid] for uuid, _ in view_dict.items()]
        random.shuffle(final_cases)
        logger.info("Got %s final cases." % len(final_cases))

        # ===== Step 2 - get final order =====
        objs_update = []
        dedup = set()
        for i, case in enumerate(final_cases):
            logger.info("[%s] %s %s %s %s", i, case.title, case.posted, case.surgeries, view_dict.get(case.uuid, 'n/a'))
            objs_update.append({'objectID': str(case.uuid), 'ranking': i+1})
            dedup.add(str(case.uuid))

        print(objs_update)

        # clear ranking
        cases = Case.objects.filter(state='published')
        for case in cases:
            uuid = str(case.uuid)
            if uuid not in dedup:
                dedup.add(uuid)
                objs_update.append({'objectID': uuid, 'ranking': 999})

        # ===== Step 3 - update ranking in algolia =====
        logger.info("Updating algolia index %s ..." % ALGOLIA_CASE_INDEX)
        client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_SECRET)
        index = client.init_index(ALGOLIA_CASE_INDEX)
        index.partial_update_objects(objs_update, {'createIfNotExists': False})
        client.close()

        logger.info("Done")
