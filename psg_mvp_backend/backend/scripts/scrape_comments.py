"""

To run:
    python manage.py runscript scrape_comments

"""

import os
import subprocess
import coloredlogs, logging


from users.clinics.models import ClinicProfile


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

URL_template = 'https://www.google.com/maps/search/?api=1&query=%s,%s&query_place_id=%s'
#SCRAPPER_SCRIPT = '/Users/erin/PycharmProjects/prototype_tools/review_data/scrapper/gl_map_review/scrape.js %s %s %s %s'
SCRAPPER_SCRIPT = '/Users/cjoun/django/review_data/scrapper/gl_map_review/scrape.js %s %s %s %s'


def run():
    skip_cnt, total = 0, 0
    lines = ''
    clinics = ClinicProfile.objects.all()
    for i, clinic in enumerate(clinics):
        clinic_name = clinic.display_name
        for branch in clinic.branches:
            total += 1
            place_id = branch.place_id
            lat, long = branch.latitude, branch.longitude
            if not branch.is_exact_place_id or not clinic_name or not place_id \
                    or not lat or not long:
                logger.warning("skip %s %s (place_id: %s, long: %s, lat: %s)"
                               % (clinic_name, branch.branch_name, place_id, long, lat))
                skip_cnt += 1
                continue

            url = URL_template % (long, lat, place_id)
            logger.info(clinic_name)
            logger.info(url)

            # os.system('node ' + SCRAPPER_SCRIPT % (clinic_name, branch.branch_name, place_id, url))
            lines += ', '.join([clinic_name, branch.branch_name, place_id, url]) + '\n'
            # break

    logger.info("%s/%s written to file" % (total-skip_cnt, total))
    with open('./urls.txt', 'w') as the_file:
        the_file.write(lines)

