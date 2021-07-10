"""
Generate a list of FB/Google review urls for all ClinicBranch objects in json format.
Two files will be outputed w/ one being success and the other errors.

To run:
    $ python manage.py runscript gen_urls

"""
import json
import pprint
import coloredlogs, logging
from urllib.parse import urljoin
from typing import Dict, List
from collections import defaultdict  # available in Python 2.5 and newer

import googlemaps
import requests
from django.conf import settings

from users.clinics.models import ClinicBranch, ClinicProfile


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

# google Maps API python client
gmaps = googlemaps.Client(key=settings.GOOGLE_MAP_API_KEY)
pp = pprint.PrettyPrinter(indent=4)

SAVE = True
URL_template = 'https://www.google.com/maps/search/?api=1&query=%s,%s&query_place_id=%s'
REVIEW_PAGE_SUFFIX = "reviews/?ref=page_internal"


def run():
    """
    Loop through each clinic object and output the FB/GL review url.

    :return:
    """
    clinics = ClinicProfile.objects.all()

    res, error = [], []
    google_clinic_branch_success_count = 0

    for i, clinic in enumerate(clinics):
        if i > 25:
            continue

        logger.info("clinic_count = %s" % i)
        if clinic.fb_url:
            _handle_fb(error, clinic, res)

        logger.info('----%s (%s branches)----' % (clinic.display_name, len(clinic.branches)))

        if len(clinic.branches) == 0:
            _handle_error(error, clinic, None, place_id, "google", "branches == 0", "")
            continue

        for branch in clinic.branches:
            if not branch:
                _handle_error(error, clinic, None, place_id, "google", "not branch", "")
                continue

            logger.info('[branch %s]' % branch.branch_name)
            place_id = branch.place_id
            # not branch.is_exact_place_id or
            # skip if no exact or no place id
            if not place_id:
                _handle_error(error, clinic, branch, place_id, "google", "not place_id", "")
                continue

            lng, lat = get_coord_from_google_map_api(error, clinic, branch, place_id)
            if lng != 0 and lat != 0:
                google_clinic_branch_success_count += 1
                url = URL_template % (lng, lat, place_id)
                res.append({
                    "source": "google",
                    "clinic_uuid": clinic.uuid,
                    "branch": branch.branch_name,
                    "placeId": place_id,
                    "url": url
                })

    logger.info("google_clinic_branch_success_count = %s; should be 937 7/5/2021" % google_clinic_branch_success_count)
    with open("./urls.success-rc1.json", 'w') as f:
        json.dump({"results": res}, f)
    with open("./urls.error-rc1.json", 'w') as f:
        json.dump({"results": error}, f)

    pp.pprint(erorr_dict)

    logger.info("should have written a file")


#######################
# Internal Functions
#######################


erorr_dict = defaultdict(int)


def _handle_error(error,clinic,branch,place_id,source,reason,url):
    logger.error(reason)

    #increment hashmap for reason failure
    erorr_dict[reason] += 1

    branchName = ""
    if branch:
        branchName = getattr(branch, 'branch_name', "")

    uuid = getattr(clinic, 'uuid', "")

    error.append({
        "branch": branchName,
        "reason": reason,
        "clinic": uuid,
        "url": url,
        "source": source,
        "placeId": place_id,
    })


def get_coord_from_google_map_api(error: List[any], clinic:ClinicProfile, branch: ClinicBranch, place_id: str):
    """
    Run the google Place API to get lontitude and latitude.

    :param place_id:
    :return:
    """
    try:
        # json format
        logger.info("place id %s" % place_id)
        rst = gmaps.place(place_id, language='zh-TW')

    except googlemaps.exceptions.ApiError as e:
        reason = "googlemaps.exceptions.ApiError / Invalid place id: %s " % str(e)
        _handle_error(error, clinic, branch, place_id, "google", reason, "")
        return 0, 0

    # update long/lat
    try:
        pp.pprint(rst)
        location_dict = rst['result']['geometry']['location']
        lng, lat = location_dict['lng'], location_dict['lat']
        logger.info('*lng: %s, lat: %s' % (lng, lat))
        return lng, lat
    except KeyError:
        _handle_error(error, clinic, branch, place_id, "google", "no long/lat found.", "")
        return 0, 0


def _url_ok(url: str) -> bool:
    """
    Check whether an url is valid.
    :param url:
    :return:
    """
    request = requests.get(url)
    if request.status_code == 200:
        return True
    return False


def _handle_fb(error: List[any], clinic: ClinicProfile,
               res: List[any]) -> Dict[str, str]:
    """

    :param clinic:
    :param res:
    :return:
    """
    #TODO: if fb_url doens't end in / append a /
    url = urljoin(clinic.fb_url, REVIEW_PAGE_SUFFIX)

    # check url works
    if not _url_ok(url):
        _handle_error(error, clinic, None, "", "facebook", "url not ok", url)
        return

    res.append({
        "source": "facebook",
        "clinic_uuid": clinic.uuid,
        "branch": "",
        "placeId": "",
        "url": url
    })
