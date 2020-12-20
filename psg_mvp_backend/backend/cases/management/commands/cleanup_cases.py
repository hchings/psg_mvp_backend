"""
Command to clean up existing cases in database when new fields created.
Use w/ cautious.

To run:
    python manage.py cleanup_cases

"""

from elasticsearch_dsl import Search, Index, connections
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
import coloredlogs, logging

from django.conf import settings
from django.db.models import F
from django.core.management.base import BaseCommand, CommandError

from cases.models import Case
from cases.doc_type import CaseDoc


# Create a logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class Command(BaseCommand):
    """
    Clean up field value of Cases when new fields are added.
    e.g., to provide initial values
    """
    help = 'Cleanup existing cases in database.'

    def handle(self, *args, **options):
        self.clean_author_posted_field()

    @classmethod
    def clean_gender_field(cls):
        pass

    @classmethod
    def clean_author_posted_field(cls):
        """
        Provide initial value to author_posted field,
        which is not on auto_new

        :return:
        """
        # Case.objects.all().update(posted=F('author_posted'))
        cases = Case.objects.all()
        # slow, will hit the db multiple times.
        # but it will not go through signals and auto update the posted field
        # as updated() is used instead of save()
        for case in cases:
            Case.objects.filter(uuid=case.uuid).update(author_posted=case.posted)
