"""
Command to bulk insert all the reviews into DB from excel sheet.


To run:
    python manage.py load_reviews


# TODO: WIP

"""
import coloredlogs, logging
from collections import Counter
import os, re

import pandas as pd
import dateparser

from django.core.management.base import BaseCommand, CommandError

from backend.settings import FIXTURE_ROOT
from backend.shared.utils import hash_text

from reviews.models import Review, Doctor
from cases.models import UserInfo, ClinicInfo
from users.clinics.models import ClinicProfile, ClinicBranch
from users.doctors.models import DoctorProfile


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


SCRAP_TIME = ''
SOURCE = 'gl'  # pls manually set this
# note that this is relevant to the top app folder
FILE_NAME = os.path.join(FIXTURE_ROOT, 'reviews_gl_0814.xlsx')


# read in excel
df = pd.read_excel(FILE_NAME)
logger.info("Review shape: %s" % str(df.shape))

# clinic name to regex
name_regex = {}

# key: clinicname+doctorname, value: doctor uuid
doctor_to_uuid = {}
surname_to_full_name = {}

collide = set()


class Command(BaseCommand):
    """

    """
    has_doctor_cnt = 0

    def handle(self, *args, **options):
        for index, row in df.iterrows():
            print("=====%s====" % index)
            # print(row)
            created = dateparser.parse(row['date'])

            user_info = UserInfo(scp=True,
                                 scp_username=row['user'].strip())

            # text
            text = row['review']
            if not text:
                continue

            # find clinic
            clinic_name, place_id = row['clinic'].strip(), row['placeId'].strip()

            # check hash
            hash = hash_text(user_info.scp_username + text)

            if Review.objects.filter(clinic={'place_id': place_id}, hash=hash):
                logger.info("review exist in db, skipped.")

            if not place_id:
                continue
            c_res = ClinicProfile.objects.filter(branches={'place_id': place_id})

            if not c_res:
                logger.error('Cannot find clinic: %s, %s' % (clinic_name, place_id))
                continue
            else:
                clinic_profile = c_res[0]
                # find branch. Seems you can't use objects on djongo's model.
                branch = None
                for b in clinic_profile.branches:
                    if b.place_id == place_id:
                        branch = b
                        break
                assert(branch is not None)

                # branch = ClinicBranch.objects.get(place_id=place_id)

            if len(c_res) > 1:
                logger.error('More than one clinic found: %s, %s' % (clinic_name, place_id))

            # find doctor WIP
            doctors = DoctorProfile.objects.filter(clinic_uuid=clinic_profile.uuid)
            doctors_objs = []

            surnames = []

            # build name regex if none
            if doctors and clinic_profile.uuid not in name_regex:
                surname_to_full_name[clinic_profile.uuid] = {}
                regex_str = r"("
                for i, doctor in enumerate(doctors):
                    key = clinic_profile.uuid + doctor.display_name
                    doctor_to_uuid[key] = doctor._id
                    # surname only
                    key = clinic_profile.uuid + doctor.display_name[0]
                    doctor_to_uuid[key] = doctor._id
                    if doctor.display_name:
                        surname_to_full_name[clinic_profile.uuid][doctor.display_name[0]] = doctor.display_name
                        surnames.append(doctor.display_name[0])
                        regex_str += doctor.display_name + "|"

                regex_str = regex_str[:-1] + ")"

                surnames_unique = []
                if surnames:
                    counter_dict = Counter(surnames)
                    for surname in surnames:
                        if counter_dict[surname] == 1:
                            surnames_unique.append(surname)

                name_regex[clinic_profile.uuid] = {
                    'regex': regex_str,
                    'surnames': surnames_unique
                }

                print("====build regex for %s" % clinic_profile)
                print(name_regex[clinic_profile.uuid])
                # print(doctor_to_uuid)
                # print(surname_to_full_name[clinic_profile.uuid])


            # TODO: it can be multiple doctors
            # surname first
            # if surnames:
            #     counter_dict = Counter(surnames)
            #     regex_str_2 = r"("
            #     for surname in surnames:
            #         if counter_dict[surname] == 1:
            #             regex_str_2 += "%s醫師|%s醫生|" % (surname, surname)
            #     regex_str_2 = regex_str_2[:-1] + ")"
            #
            #     print(regex_str_2)
            #     res = re.findall(regex_str_2, text)
            #     if res:
            #         print(res)
            #
            #
            # print(regex_str)
            res = re.findall(regex_str, text)

            surnames_copy = name_regex.get(clinic_profile.uuid, {}).get('surnames', []).copy()
            if res:
                print("res1", res)
                self.has_doctor_cnt += 1
                for name in res:
                    # create doctor obj
                    key = clinic_profile.uuid + name
                    obj = Doctor(name=name, profile_id=doctor_to_uuid[key])
                    doctors_objs.append(obj)

                    # pop already matched name
                    if name:
                        try:
                            surnames_copy.remove(name[0])
                            print("pop ", name[0])
                        except ValueError:
                            pass

            if surnames_copy:
                regex_str_2 = "("
                for surname in surnames_copy:
                    regex_str_2 += "%s醫師|%s醫生|" % (surname, surname)

                regex_str_2 = regex_str_2[:-1] + ")"

                # print(regex_str_2)
                res = re.findall(regex_str_2, text)
                if res:
                    print(regex_str_2)
                    print("res2", res)
                    self.has_doctor_cnt += 1
                    for name in set(res):
                        key = clinic_profile.uuid + name[0]
                        obj = Doctor(name=surname_to_full_name[clinic_profile.uuid][name[0]], profile_id=doctor_to_uuid[key])
                        doctors_objs.append(obj)

            if doctors_objs:
                print("------doctors: ", doctors_objs)

            # barnch_name = '',
            clinic_info = ClinicInfo(display_name=clinic_profile.display_name,
                                     place_id=place_id,
                                     branch_name=branch.branch_name,
                                     uuid=clinic_profile.uuid)
            text = text.strip()
            # specific for google
            if text.startswith('(Translated by Google)'):
                text = text.split(')')[1].strip()

            # rating
            rating = row['rating'].strip()
            if rating:
                try:
                    rating = int(rating.split(' ')[0])
                except ValueError as e:
                    # can't parse int
                    logger.error('load_review parse rating error: ' + str(e))
                    rating = 0

            # TODO: how to link to branch
            # TODO: scarpe data to 6 dimensions --> this is the only part that might need NLP

            # for checking hash
            if hash in collide:
                logger.error("Hash collide, ", clinic_profile.display_name)
            else:
                collide.add(hash)

            review = Review(hash=hash,
                            scp_time=created,
                            author=user_info,
                            clinic=clinic_info,
                            body=text,
                            doctors=doctors_objs,
                            rating=rating,
                            source=SOURCE)
            review.save()

            # if index > 1000:
            #     break

            # print("has doctor", self.has_doctor_cnt)
