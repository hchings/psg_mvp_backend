"""
Clean up the services_raw field in ClinicProfile.

>> python manage.py cleanup_clinic_services

"""
import coloredlogs, logging
import re
from string import digits, punctuation

from django.core.management.base import BaseCommand

from users.clinics.models import ClinicProfile


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

GENERICS = ("醫學美容", "臉部", "乳房", "私密", "熱門療程", "美容治療")

STOPWORDS = ["熱門", "介紹", "越", "自己", "讓", "女孩", "學習", "找", "案例", "改善", "外科",
             "沒", "官", "項目", "其他", "無醫美", "五大", "諮詢", "專業"]


class Command(BaseCommand):
    """
    Cleanup services in ClinicProfile.
    """
    help = 'Cleanup services in ClinicProfile'


    def handle(self, *args, **options):
        objs = ClinicProfile.objects.all()
        logger.info("%s clinics" % len(objs))
        for i, obj in enumerate(objs):
            if obj.services_raw_input and not obj.services_raw:
                logger.error("NOT indexed")

            if ('無醫美' in obj.services_raw_input or "永久停業" in obj.services_raw_input) and not obj.is_oob:
                logger.warning("Mark %s as obsolete." % obj.display_name)
                obj.is_oob = True
                obj.save()

            services_raw_cleaned = []
            dedup = set()
            for service in obj.services_raw:
                # remove crappy entries
                drop = False
                for stopword in STOPWORDS:
                    if stopword in service:
                        logger.warning("drop(1) %s" % service)
                        drop = True
                        break

                if drop:
                    continue

                # remove str in brackets
                service = re.sub(r"\([^()]*\)", "", service)
                service = re.sub(r"\([^()]*\)", "", service)
                service = re.sub(r"\（[^()]*\）", "", service)
                service = re.sub(r"新一代|高科技", "", service)
                service = service.lstrip(digits).strip()
                service = service.lstrip(punctuation).strip()


                tokens = re.split('、|/|\.|，|:|：', service)
                for token in tokens:
                    if not re.search('[a-zA-Z]+', token) and len(token) > 15:
                        logger.warning("drop(2) %s" % token)
                        continue

                    if len(token) > 1 and token not in GENERICS and token not in dedup:
                        token = ''.join(e for e in token if e.isalnum())
                        if len(token) > 4:
                            token = re.sub(r"手術", "", token)
                            token = re.sub(r"整形", "", token)
                        dedup.add(token)
                        services_raw_cleaned.append(token)


            if services_raw_cleaned is not obj.services_raw:
                logger.info("======[%s] clinic: %s=====" % (i, obj.display_name))
                logger.info("before: %s" % obj.services_raw)
                logger.info("after: %s" % services_raw_cleaned)


            else:
                logger.info("======[%s] clinic: %s [No changes]=====" % (i, obj.display_name))
                logger.info(obj.services_raw)


            obj.services_raw = services_raw_cleaned
            # obj.services_raw_input = ", ".join(services_raw_cleaned)
            obj.save()
