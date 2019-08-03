"""
Get the latest place details from Google Place API
for all ClinicBranch objects and update the corresponding fields.

To run:
    $ python manage.py fill_place_info

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


def run():
    clinics = ClinicProfile.objects.all()

    for clinic in clinics:
        logger.info('----%s (%s branches)----'
                    % (clinic.display_name, len(clinic.branches)))
        for branch in clinic.branches:
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
                rst = gmaps.place(place_id, language='zh-TW')

            except googlemaps.exceptions.ApiError:
                logger.error('Invalid place id.')
                # raise PlaceInfoException('Invalid place id.')

            # update rating
            try:
                rating = rst['result']['rating']
                branch.rating = rating
                logger.info('*rating: %s' % rating)
            except KeyError:
                logger.error('no rating found.')

            # update long/lat
            try:
                location_dict = rst['result']['geometry']['location']
                lng, lat = location_dict['lng'], location_dict['lat']
                branch.longitude, branch.latitude = lng, lat
                logger.info('*lng: %s, lat: %s' % (lng, lat))
                # branch.rating = rst['result']['rating']
            except KeyError:
                logger.error('no long/lat found.')

            # update address (full)
            # TODO: google's address is not very cleaned.
            # TODO: most of the time you have to manually clean it for now.
            # try:
            #     if deep or not getattr(obj, 'address', None):
            #         address = rst['result']['formatted_address']
            #         # TODO: plz write a better regex...
            #         obj.address = address.lstrip('0123456789.-')
            # except AttributeError:
            #     pass

            # update region (i.e., city)
            # adr_address = rst['result']['adr_address']

            # TODO: make the regex more robust..
            # try:
            #     if deep or not getattr(obj, 'region', None):
            #         re_rst = re.search(r'"region">(.*?)<',
            #                            adr_address)
            #         if re_rst:
            #             obj.region = re_rst.group(1)
            # except AttributeError:
            #     pass

            # update locality (i.e., district)
            # TODO: add google trans cause sometimes the API returns simplified Chinese
            # try:
            #     if deep or not getattr(obj, 'locality', None):
            #         re_rst = re.search(r'"locality">(.*?)<',
            #                            adr_address)
            #         if re_rst:
            #             obj.locality = re_rst.group(1)
            # except AttributeError:
            #     pass

            # update phonenumber
            # try:
            #     if deep or not getattr(obj, 'phone', None):
            #         # TODO: deal with nationality code here
            #         obj.phone = '+886' + rst['result']['formatted_phone_number']
            # except (AttributeError, KeyError):
            #     pass

            # update opening_hours
            weekday_text = rst['result'].get('opening_hours', {}).get('weekday_text', [])
            if not weekday_text:
                logger.warning('No opening info for %s' % branch.branch_name)
            else:
                # 'weekday_text': ['星期一: 11:00–20:00', '星期二: 11:00–20:00', '星期三: 11:00–20:00', '星期四: 11:00–20:00',
                #                  '星期五: 11:00–20:00', '星期六: 11:00–20:00', ' 星期日: 休息']}
                branch.opening_info = str(weekday_text)
                logger.info('*Opening info: %s' % branch.opening_info)
                info_dict = {}
                for item in weekday_text:
                    day_cn, time_span = re.split(':\s+', item)
                    day = _get_day_number(day_cn)
                    if time_span == '休息':
                        time_span = 'close'
                    if time_span not in info_dict:
                        info_dict[time_span] = [day]
                    else:
                        info_dict[time_span].append(day)

                logger.info('*Opening info [concise]: %s' % json.dumps(info_dict))
                branch.opening_concise = json.dumps(info_dict)
                # obj.opening_info = json.dumps(info_dict)

        if SAVE:
            clinic.save()
            logger.info('Saved.')


def _get_day_number(day_cn):
    """
    trad chinese day to arabic number
    :param day_cn (str):
    :return (int):
    """
    if day_cn == '星期一':
        return 1
    elif day_cn == '星期二':
        return 2
    elif day_cn == '星期三':
        return 3
    elif day_cn == '星期四':
        return 4
    elif day_cn == '星期五':
        return 5
    elif day_cn == '星期六':
        return 6
    else:
        return 0 # Sunday
