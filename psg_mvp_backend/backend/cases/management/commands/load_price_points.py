"""
Load scrapped price points from excel into db

>> python manage.py load_price_points

"""
import coloredlogs, logging
import re
from datetime import datetime

import pandas as pd
import boto3
from annoying.functions import get_object_or_None
from django.core.management.base import BaseCommand


from users.clinics.models import ClinicProfile
from cases.models import PricePoint, SurgeryTag, SurgeryMeta

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class Command(BaseCommand):
    """
    Cleanup services in ClinicProfile.
    """
    help = ''

    def handle(self, *args, **options):
        s3 = boto3.client('s3')

        response = s3.get_object(Bucket='sagemaker-studio-hkwar4uafz8',
                                 Key="freelancing-price-point.xlsx")
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        if status == 200:
            logger.info(f"Successful S3 get_object response. Status - {status}")
            df = pd.read_excel(response.get("Body"))
            df.fillna(0, inplace=True)
            logger.info(df.head())
        else:
            logger.error(f"Unsuccessful S3 get_object response. Status - {status}")
            return

        for index, row in df.iterrows():
            if not row["link"]:
                continue
            # check existence

            clinic_obj = get_object_or_None(ClinicProfile, display_name=row["clinicname"])
            if clinic_obj is None or not clinic_obj.uuid:
                logger.error("Clinic %s not found" % row["clinicname"])
                continue

            price_obj = get_object_or_None(PricePoint,
                                           clinic_uuid=clinic_obj.uuid,
                                           ori_url=row["link"],
                                           surgery_meta={'min_price': int(row['min'] or 0) or None,
                                                         'max_pricee': int(row['max'] or 0) or None})
            # check existence
            if price_obj is not None:
                logger.warning("Price point from %s already exist" % row["link"])
                # TODO: tmp
                # price_obj.delete()

            surgeries_objs = []
            for surgery in re.split("，|,", row['service']):
                surgery_tag = SurgeryTag(name=surgery.strip(), mat='')
                surgeries_objs.append(surgery_tag)


            datetime_obj = datetime.strptime(str(row['year/month']).split()[0], "%Y-%m-%d")
            price_obj = PricePoint(
                clinic_uuid=clinic_obj.uuid,
                surgeries=surgeries_objs,
                surgery_meta=SurgeryMeta(year=int(datetime_obj.year) or None,
                                         month=int(datetime_obj.month) or None,
                                         min_price=int(row['min'] or 0) or None,
                                         max_price=int(row['max'] or 0) or None),
                ori_url=row["link"])
            price_obj.save()
