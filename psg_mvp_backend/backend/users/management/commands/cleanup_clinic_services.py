"""
Clean up the services_raw field in ClinicProfile.

>> python manage.py cleanup_clinic_services

"""
import coloredlogs, logging

from django.core.management.base import BaseCommand

from users.clinics.models import ClinicProfile


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class Command(BaseCommand):
    """
    Cleanup services in ClinicProfile.
    """
    help = 'Cleanup services in ClinicProfile'


    def handle(self, *args, **options):
        objs = ClinicProfile.objects.all()
        print("%s clinics", len(objs))
        for i, obj in enumerate(objs):
            if obj.services_raw_input and not obj.services_raw:
                print("NOT indexed")

            if '無醫美' in obj.services_raw_input and not obj.is_oob:
                logger.info("Mark %s as obsolete." % obj.display_name)
                obj.is_oob = True
                obj.save()


            # clean up service_raw
            # TODO: WIP
            changed = False
            services_raw_cleaned = []
            for item in obj.services_raw:
                items = item.split("、")
                if len(items) > 1:
                    changed = True
                    concate = False
                    for token in items:
                        if len(token) <= 2:
                            concate = True
                services_raw_cleaned += items



            if changed:
                print("======clinic: %s=====" % obj.display_name)
                print("before:", obj.services_raw)
                print("after:", services_raw_cleaned)



