"""
Command to create the

To run:
    python manage.py monitor_cases

"""

from elasticsearch_dsl import Search, Index, connections
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
import coloredlogs, logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from users.clinics.models import ClinicProfile


# Create a logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class Command(BaseCommand):
    """
    Delete the exisiting cases index in ES instance
    and bulk insert all "published" cases from main DB.
    """

    help = 'Indexes Cases in Elastic Search'

    def handle(self, *args, **options):
        self.load_index(wipe_out=True)

        res = ClinicProfile.objects.all()





        # clinic no logo
        # clinic name 未知
        # no clinic profile
        # no, test clinic link
        # case tag?


        # random view
        # adjust timestamp




    @staticmethod
    def load_index(wipe_out=False):
        es = Elasticsearch(
            [{'host': settings.ES_HOST, 'port': settings.ES_PORT}],
            index="cases"
        )
        cases_index = Index('cases', using='default')
        cases_index.document(CaseDoc)  # doc_type has been deprecated
        if wipe_out and cases_index.exists():
            cases_index.delete()
            logger.warning("Deleted Cases Index.")
        CaseDoc.init()

        result = bulk(
            client=es,
            actions=(case.indexing() for case in Case.objects.all().iterator() if case.state == 'published')
        )

        logger.info("Indexed cases: %s" % str(result))
