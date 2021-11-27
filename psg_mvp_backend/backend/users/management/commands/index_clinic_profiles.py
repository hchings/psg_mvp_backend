"""
[Obsolete]
Command to create the index of Clinic Profile
and bulk insert all the current documents in the ClinicProfile collections.
This will create branch-level documents into the ES engine.

To run:
    python manage.py index_clinic_profiles

"""

import itertools

from elasticsearch_dsl import Search, Index, connections
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
import coloredlogs, logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from users.clinics.models import ClinicProfile
from users.doc_type import ClinicProfileDoc


# Create a logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class Command(BaseCommand):
    help = 'Indexes Clinic Profiles in Elastic Search'

    def handle(self, *args, **options):
        es = Elasticsearch(
            [{'host': settings.ES_HOST, 'port': settings.ES_PORT}],
            index="clinic_profile"
        )
        clinic_profile_index = Index('clinic_profile', using='default')
        clinic_profile_index.document(ClinicProfileDoc)  # doc_type has been deprecated
        if clinic_profile_index.exists():
            clinic_profile_index.delete()
            logger.warning("Deleted Clinic Profile Index.")
        ClinicProfileDoc.init()

        # flatten the list
        data = list(itertools.chain.from_iterable([clinic_profile.indexing()
                                                   for clinic_profile
                                                   in ClinicProfile.objects.all().iterator()]))

        result = bulk(
            client=es,
            actions=data
        )
        logger.info("Indexed clinic profiles: %s" % str(result))
