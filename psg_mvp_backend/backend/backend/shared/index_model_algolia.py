"""
Index cases into Algolia

>> python manage.py index_model_algolia

"""
import coloredlogs, logging
from abc import ABC, abstractmethod

from algoliasearch.search_client import SearchClient

from django.core.management.base import BaseCommand
from backend.settings import ALGOLIA_APP_ID, ALGOLIA_SECRET


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class Command(ABC, BaseCommand):
    """
    Index published clinics into Algolia.
    """

    @property
    @abstractmethod
    def index_name(self):
        pass

    @property
    @abstractmethod
    def model_serializer(self):
        pass

    @property
    @abstractmethod
    def model_class(self):
        pass

    def handle(self, *args, **options):
        client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_SECRET)

        # index_name = ALGOLIA_CLINIC_INDEX
        index = client.init_index(self.index_name)
        logger.info("Loading to Algolia index: %s" % self.index_name)

        # is_oob = False
        logger.info("option: %s" % options)
        objs = self.model_class.objects.filter(**options)

        if self.index_name.endswith('dev'):
            # limit dev records in algolia for dev mode to avoid cost
            objs = objs[:1000]

        logger.info("indexing %s %ss..." % (len(objs),
                                            self.model_class.__name__.lower()))
        serializer = self.model_serializer(objs,
                                      many=True,
                                      indexing_algolia=True)

        logger.info("Indexed %s %ss..." % (len(objs),
                                           self.model_class.__name__.lower()))

        data = []
        for record in serializer.data:
            if record['uuid']:
                data.append(record)
            else:
                logger.error("%s %s has no uuid!" % (self.model_class.__name__,
                                                     record['display_name']))

        index.replace_all_objects(data)
        logger.info("done")
        client.close()
