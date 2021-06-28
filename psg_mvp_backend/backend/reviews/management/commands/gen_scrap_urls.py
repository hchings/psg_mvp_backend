"""
Command to generate urls to scrape.

To run:
    python manage.py gen_scrap_urls

"""

import logging
from urllib.parse import urljoin

import requests

from django.core.management.base import BaseCommand, CommandError

from users.clinics.models import ClinicProfile


logger = logging.getLogger(__name__)
REVIEW_PAGE_SUFFIX = "reviews/?ref=page_internal"


class Command(BaseCommand):
    def handle(self, *args, **options):
        clinic_profiles = ClinicProfile.objects.all()
        logger.info("%s clinics" % len(clinic_profiles))

        cnt = 0
        res = []
        for clinic in clinic_profiles:
            if not clinic.fb_url:
                continue

            url = urljoin(clinic.fb_url, REVIEW_PAGE_SUFFIX)
            # print("url", url)

            # check url works
            if not self._url_ok(url):
                continue

            cnt += 1
            res.append("%s %s %s" % (clinic.uuid, clinic.display_name, url) )


        # logger.info("%s valid review URLs found." % cnt)
        print("%s valid review URLs found." % cnt)
        with open('./fb_urls.txt', 'w') as f:
            for item in res:
                f.write("%s\n" % item)


    @staticmethod
    def _url_ok(url):
        request = requests.get(url)
        if request.status_code == 200:
            return True
        return False
