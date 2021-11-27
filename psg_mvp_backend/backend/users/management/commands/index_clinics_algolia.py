"""
Index cases into Algolia

>> python manage.py index_clinics_algolia <clinics-brief-dev>

"""
import coloredlogs, logging
from algoliasearch.search_client import SearchClient

from django.core.management.base import BaseCommand

from users.clinics.models import ClinicProfile
from users.clinics.serializers import ClinicCardSerializer

from backend.settings import ALGOLIA_APP_ID, ALGOLIA_SECRET, \
    ALGOLIA_CLINIC_INDEX

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class Command(BaseCommand):
    """
    Index published clinics into Algolia.
    """

    help = 'Indexes Clinics in Algolia Search'

    def add_arguments(self, parser):
        parser.add_argument("index_name",
                            type=str,
                            nargs='?',
                            default=ALGOLIA_CLINIC_INDEX,
                            help="The index name in Algolia. Use 'clinics-brief-dev' for dev and 'clinics-brief-prod' for prod.")

    def handle(self, *args, **options):
        client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_SECRET)
        index_name = options["index_name"]
        index = client.init_index(index_name)
        logger.info("Loading to Algolia index: %s" % index_name)

        objs = ClinicProfile.objects.filter(is_oob=False)
        logger.info("indexing %s clinics..." % len(objs))
        serializer = ClinicCardSerializer(objs,
                                          many=True,
                                          indexing_algolia=True)

        logger.info("Indexed %s clinics..." % len(objs))

        data = []
        for clinic in serializer.data:
            if clinic['uuid']:
                data.append(clinic)
            else:
                logger.error("clinic %s has no uuid!" % clinic['display_name'])

        index.replace_all_objects(data)
        logger.info("done")
        client.close()
