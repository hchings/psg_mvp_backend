"""
Create random seed for post date and hitcount for published cases.

To generate or update hitcount file:
    python manage.py random_seed --overwrite=True

To update post time or author_post time:
    python manage.py random_seed --update-time=True

"""
import json, os
import datetime
from random import randint
from dateutil.relativedelta import relativedelta

import coloredlogs, logging

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from cases.models import Case

from backend.settings import FIXTURE_ROOT

# Create a logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


HITCOUNT_FILE = os.path.join(FIXTURE_ROOT, 'hitcount.json')


class Command(BaseCommand):
    """
    Create random seed for post date and hitcount for published cases.
    """

    help = 'Create random seed for post date and hitcount for published cases.'
    overwrite = False
    update_time = False

    def add_arguments(self, parser):
        # TODO: not working
        parser.add_argument('--update-time', default=False)
        parser.add_argument('--overwrite', default=False)

    def handle(self, *args, **options):
        self.overwrite = options.get('overwrite', False)
        self.update_time = options.get('update-time', False)

        if not self.update_time:
            logger.info('overwrite mode: %s' % self.overwrite)
            self.initialize_hit_count()
        else:
            logger.info('updating post time: %s' % self.overwrite)
            self.update_post_time()


    def initialize_hit_count(self):
        """
        Generate or update initial hitcount in a json file
        under fixture/

        :return:
        """
        # read existing file
        hitcount_dict = {}
        try:
            with open(HITCOUNT_FILE) as json_file:
                hitcount_dict = json.load(json_file)
        except FileNotFoundError:
            logger.info('hitcount file not found at %s, re-generating one...' % HITCOUNT_FILE)

        # Case.objects.all().update(posted=F('author_posted'))
        cases = Case.objects.filter(state='published')

        for case in cases:
            if case in hitcount_dict and not self.overwrite:
                # already have an initial value, don't overwrite
                continue

            interest = case.interest or 0
            initial_value = 0

            if interest < 4:
                initial_value = randint(30, 120)
            elif interest < 7:
                initial_value = randint(300, 700)
            else:
                initial_value = randint(900, 1500)

            hitcount_dict[str(case.uuid)] = initial_value

        print(hitcount_dict)

        with open(HITCOUNT_FILE, 'w') as fp:
            json.dump(hitcount_dict, fp, indent=4, sort_keys=True)


    def update_post_time(self):
        """
        Add 3 or 5 months to cases whose author_posted or posted
        are earlier in Nov 2020.

        :return:
        """
        # TODO: temp hardcoded
        d = datetime.date(2020, 11, 1)
        cases = Case.objects.filter(Q(posted__lte=d) | Q(author_posted__lte=d))

        logger.info('%s cases updated prior to %s, their author_posted or posted fields will be changed...' %
                    (len(cases), d))

        mon_rel_3 = relativedelta(months=3)
        mon_rel_6 = relativedelta(months=6)

        for case in cases:
            if case.author_posted:
                if int(case.author_posted.month) < 6:
                    case.author_posted = case.author_posted + mon_rel_6
                else:
                    case.author_posted = case.author_posted + mon_rel_3
            else:
                if int(case.posted.month) < 6:
                    case.posted = case.posted + mon_rel_6
                else:
                    case.posted = case.posted + mon_rel_3

            case.save()
