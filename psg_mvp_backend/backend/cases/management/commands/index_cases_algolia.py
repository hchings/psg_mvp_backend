"""
Index cases into Algolia

>> python manage.py index_cases_algolia <index_name>

"""
import coloredlogs, logging
from algoliasearch.search_client import SearchClient

from django.core.management.base import BaseCommand
from backend.settings import ALGOLIA_APP_ID, ALGOLIA_SECRET, \
    FIXTURE_ROOT, ALGOLIA_CASE_INDEX

from cases.serializers import CaseCardSerializer
from cases.models import Case

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class Command(BaseCommand):
    """
    Index published cases into Algolia.
    """

    help = 'Indexes Cases in Algolia Search'

    def add_arguments(self, parser):
        parser.add_argument("index_name",
                            type=str,
                            nargs='?',
                            default=ALGOLIA_CASE_INDEX,
                            help="The index name in Algolia. Use 'cases' for us_demo and 'cases-prod' for prod website in TW")


    def handle(self, *args, **options):
        client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_SECRET)
        index_name = options["index_name"]
        index = client.init_index(index_name)
        logger.info("Loading to Algolia index: %s" % index_name)

        cases = Case.objects.filter(state="published")
        serializer = CaseCardSerializer(cases,
                                        many=True,
                                        search_view=True,
                                        indexing_algolia=True)

        logger.info("indexing %s cases..." % len(cases))
        index.replace_all_objects(serializer.data)
        logger.info("done")
        client.close()
