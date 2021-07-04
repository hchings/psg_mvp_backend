"""
Get the latest place details from Google Place API
for all ClinicBranch objects and update the corresponding fields.

To run:
    $ python manage.py runscript gen_urls

"""

import re
import json
import pprint
import coloredlogs, logging

import googlemaps

from django.conf import settings

from users.clinics.models import ClinicBranch, ClinicProfile


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


# google Maps API python client
gmaps = googlemaps.Client(key=settings.GOOGLE_MAP_API_KEY)
pp = pprint.PrettyPrinter(indent=4)

SAVE = True


class PlaceInfoException(Exception):
    """Custom exception for place info"""
    pass

URL_template = 'https://www.google.com/maps/search/?api=1&query=%s,%s&query_place_id=%s'

def handleGoogleUrl(res):
    pass

def run():

    clinics = ClinicProfile.objects.all()

    res = []
    success_count, branch_count = 0, 0

    handleGoogleUrl(res)
    print(res)
    quit()

    for i, clinic in enumerate(clinics):
        print("clinic_count = %s" % i)

        # if i > 5:
        #     break    # break here
        logger.info('----%s (%s branches)----' % (clinic.display_name, len(clinic.branches)))
        for branch in clinic.branches:
            branch_count += 1

            if not branch:
                continue
            logger.info('[branch %s]' % branch.branch_name)
            place_id = branch.place_id
            # skip if no exact or no place id
            if not branch.is_exact_place_id or not place_id:
                logger.warning('No exact place_id for %s' % branch.branch_name)
                continue

            # run the google Place API
            try:
                # json format
                print("place id %s" % place_id)
                rst = gmaps.place(place_id, language='zh-TW')

            except googlemaps.exceptions.ApiError as e:
                logger.error('Invalid place id.')
                logger.error(e)
                continue
                # raise PlaceInfoException('Invalid place id.')

            # update long/lat
            try:
                pp.pprint(rst)
                location_dict = rst['result']['geometry']['location']
                lng, lat = location_dict['lng'], location_dict['lat']
                logger.info('*lng: %s, lat: %s' % (lng, lat))
                success_count += 1
                url = URL_template % (lng, lat, place_id)
                res.append("%s,%s,%s,%s" % (clinic.display_name, branch.branch_name, place_id, url ))
            except KeyError:
                logger.error('no long/lat found.')

    print("%s valid review URLs found: %s total branches attemptes" % (success_count, branch_count))
    with open('./google_urls.txt', 'w') as f:
        for item in res:
            f.write("%s\n" % item)

    print("should have written a file")
        # if SAVE:
        #     clinic.save()
        #     logger.info('Saved.')
