"""
Command to create the index of Cases
and bulk insert all the current documents in the Cases collections.

Note that you need to specify index='cases' on any search.

To run:
    python manage.py index_cases

"""

from elasticsearch_dsl import Search, Index, connections
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
import coloredlogs, logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from cases.models import Case
from cases.doc_type import CaseDoc


# Create a logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class Command(BaseCommand):
    """
    Delete the exisiting cases index in ES instance
    and bulk insert all cases from main DB.
    """

    help = 'Indexes Cases in Elastic Search'

    def handle(self, *args, **options):
        es = Elasticsearch(
            [{'host': settings.ES_HOST, 'port': settings.ES_PORT}],
            index="cases"
        )
        cases_index = Index('cases', using='default')
        cases_index.document(CaseDoc)  # doc_type has been deprecated
        if cases_index.exists():
            cases_index.delete()
            logger.warning("Deleted Cases Index.")
        CaseDoc.init()

        result = bulk(
            client=es,
            actions=(case.indexing() for case in Case.objects.all().iterator())
        )

        logger.info("Indexed cases: %s" % str(result))
