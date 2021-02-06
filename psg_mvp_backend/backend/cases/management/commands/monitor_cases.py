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

from cases.models import Case
from cases.doc_type import CaseDoc
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
        # self.load_index(wipe_out=True)

        cases = Case.objects.filter(state='published')
        missing_clinic_profile = set()
        missing_logo = set()

        for case in cases:
            clinic_id = case.clinic.uuid
            display_name = case.clinic.display_name
            if not clinic_id and display_name and display_name not in missing_clinic_profile:
                # print
                missing_clinic_profile.add(display_name)
                print("Missing clinic profile: %s" % display_name)

            if clinic_id:
                clinic_profile = ClinicProfile.objects.get(uuid=case.clinic.uuid)
                if clinic_id not in missing_logo and not clinic_profile.logo:
                    missing_logo.add(clinic_id)
                    print("Missing: logo", clinic_profile.display_name)

        # clinic no logo
        # clinic name 未知
        # no clinic profile
        # no, test clinic link
        # case tag?


        # random view
        # adjust timestamp
