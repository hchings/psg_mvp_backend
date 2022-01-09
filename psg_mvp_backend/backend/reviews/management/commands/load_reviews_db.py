"""
Command to bulk insert all the reviews into DB from excel sheet.
Reviews csv format is expected to be comply w/ the output of nlp-engine

To run:
    python manage.py load_reviews_db

Example:
    python manage.py load_reviews_db all_reviews_done.csv "Sep 2021"

"""
import coloredlogs, logging
import os
from ast import literal_eval
import pprint

import pandas as pd
import numpy as np
import dateparser
from dateparser import parse

from django.core.management.base import BaseCommand, CommandError

from backend.settings import FIXTURE_ROOT
from backend.shared.utils import hash_text

from reviews.models import Review, Doctor, ReviewTopic
from cases.models import UserInfo, ClinicInfo
from users.clinics.models import ClinicProfile, ClinicBranch


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

pp = pprint.PrettyPrinter(indent=4)

TOPICS = ['topics', 'consult', 'env', 'price', 'service', 'skill']


class Command(BaseCommand):
    """

    """
    has_doctor_cnt = 0

    def add_arguments(self, parser):
        parser.add_argument("input_review_file",
                            type=str,
                            help="The file name of the review CSV file processed by the Nlp-engine.")
        parser.add_argument("scrapped_date",
                            type=str,
                            help="The rough <Month Year> when the reviews were scrapped. e.g., 'Sep 2021'")

    def handle(self, *args, **options):
        input_review_file = options["input_review_file"]
        input_review_file_path =  os.path.join(FIXTURE_ROOT, input_review_file)
        scrapped_date = options["scrapped_date"]

        # read in excel
        df = pd.read_csv(input_review_file_path)

        # ensure columns and data shape
        assert(pd.Series(['user', 'date', 'rating', 'review',
                         'image', 'clinic_uuid', 'place_id',
                         'src', 'procedure', 'drop'] + TOPICS).isin(df.columns).all())

        # remove dropped reviews
        df = df.loc[df["drop"].isnull()]
        time_delta = parse("today") - parse(scrapped_date)
        logger.info("%s review shape found in %s." % (str(df.shape[0]), input_review_file_path))
        logger.info("Scrapped date :%s\n delta=%s" % (parse(scrapped_date), time_delta))

        # store review obj in db
        for index, row in df.iterrows():
            logger.info("=====%s====" % index)
            # 1. check basic info
            text = row['review']

            clinic_uuid, place_id = str(row['clinic_uuid']).strip(), str(row['place_id']).strip()

            if not text or not clinic_uuid  or text is np.nan \
                    or clinic_uuid is np.nan:
                logger.warning("review, clinic_uuid, or place_id missing. Skip.")
                continue

            text = text.strip()
            source = row["src"].lower()

            if source == 'Google':
                text = self._clean_text(text)

            #    check whether the review already exist using hash
            user_info = UserInfo(scp=True,
                                 scp_username=row['user'].strip())
            hash = hash_text(user_info.scp_username + text)
            # objs = Review.objects.filter(clinic={'place_id': place_id}, hash=hash)
            objs = Review.objects.filter(clinic={'uuid': clinic_uuid}, hash=hash)
            if objs:
                if 'Google' in text or '翻譯' in text:
                    objs[0].delete()
                    ori_text = text
                    text = text.split("(原始評論)")[0]
                    text = text.replace("(由 Google 提供翻譯)", "").strip()
                    logger.warning("[Delete review] %s -> %s" % (ori_text, text))
                else:
                    logger.warning("review exist in db, skipped.")
                    continue

            try:
                if place_id and place_id != np.nan and place_id != "nan":
                    clinic_profile = ClinicProfile.objects.get(branches={'place_id': place_id})

                    # find branch. Seems you can't use objects on djongo's model.
                    branch = None
                    for b in clinic_profile.branches:
                        if b.place_id == place_id:
                            branch = b
                            break
                else:
                    clinic_profile = ClinicProfile.objects.get(uuid=clinic_uuid)
                    branch = clinic_profile.branches[0]
                    place_id = branch.place_id
                    logger.info("Using place_id from branch %s" % branch.branch_name)
            except Exception as e:
                logger.error('Cannot find clinic uuid: %s with place_id %s: %s' % (clinic_uuid, place_id, str(e)))
                continue

            assert(branch is not None)
            clinic_info = ClinicInfo(display_name=clinic_profile.display_name,
                                     place_id=place_id,
                                     branch_name=branch.branch_name,
                                     uuid=clinic_profile.uuid)

            # 2. fill out info
            try:
                created = dateparser.parse(row['date']) - time_delta
                logger.info("%s -> %s" % (row['date'], created))
            except TypeError as e:
                logger.error("Missing date: %s" % str(e))
                continue

            # specific for google
            if text.startswith('(Translated by Google)'):
                text = text.split(')')[1]

            # rating
            try:
                rating = row['rating'].strip()
            except Exception:
                # Facebook.  bad hack
                rating = row['ratings']
                if rating:
                    rating = "5"
                else:
                    rating = "1"

            if rating:
                try:
                    rating = int(rating.split(' ')[0])
                except ValueError as e:
                    # can't parse int
                    logger.error('load_review parse rating error: ' + str(e))
                    rating = 0

            # procedure
            services = []
            if row["procedure"] and not isinstance(row["procedure"], float) and row["procedure"] != "NaN":
                services = [item.strip() for item in row["procedure"].split(",")]

            # topic
            topics_objs = []
            if row["topics"] and not isinstance(row["topics"], float) and row["topics"] != "NaN":
                topics = literal_eval(row["topics"])
                for topic in topics:
                    if row[topic] is not None and row[topic] != np.nan:
                        try:
                            sentiment = int(row[topic])
                        except Exception:
                            sentiment = None
                    else:
                        sentiment = None #unsure

                    topics_objs.append(ReviewTopic(topic=topic, sentiment=sentiment))

            review = Review(hash=hash,
                            scp_time=created,
                            scp_user_pic="",
                            author=user_info,
                            clinic=clinic_info,
                            body=text,
                            rating=rating,
                            services=services,
                            topics=topics_objs,
                            source=source)

            pp.pprint({
                "hash": hash,
                "scp_time": created,
                "author": user_info,
                "clinic": clinic_info,
                "body": text,
                "rating": rating,
                "services": services,
                "topics": topics_objs,
                "source": source
            })

            review.save()

            # read img
            if row["image"] and row["image"] != "nan" and row["image"] is not np.nan:
                img_name = row["image"].split("/")[-1] + '.png'
                img_path = os.path.join(source.capitalize(), img_name)
                logger.info("saving image from %s..." % img_path)
                try:
                    with open(os.path.join(FIXTURE_ROOT, img_path), 'rb') as f:
                        review.scp_user_pic.save("user_profile", f)
                except FileNotFoundError as e:
                    logger.error("File not found: %s" % str(e))
            # if index > 5:
            #   break

    @staticmethod
    def _clean_text(text):
        if 'Google' in text or '翻譯' in text:
            text = text.split("(原始評論)")[0]
            text = text.replace("(由 Google 提供翻譯)", "").strip()

        return text
