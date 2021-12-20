"""
Initialize the values of business types in ClinicProfile
    >> python manage.py ini_biz_types

"""
import coloredlogs, logging

from django.core.management.base import BaseCommand

from users.clinics.models import ClinicProfile

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)



class Command(BaseCommand):
    """
    Initialize the values of business types in ClinicProfile.
    """
    help = 'Initialize the values of business types in ClinicProfile'


    def handle(self, *args, **options):
        objs = ClinicProfile.objects.all()
        for obj in objs:
            clinic_name = obj.display_name
            if '皮膚' in clinic_name:
                obj.biz_type = ClinicProfile.BIZ_TYPES[1][0]
            elif '醫院' in clinic_name:
                obj.biz_type = ClinicProfile.BIZ_TYPES[2][0]
                print("%s --> %s"  % (clinic_name, ClinicProfile.BIZ_TYPES[2][0]))
            elif '眼科' in clinic_name:
                obj.biz_type = ClinicProfile.BIZ_TYPES[3][0]
                print("%s --> %s"  % (clinic_name, ClinicProfile.BIZ_TYPES[3][0]))
            else:
                obj.biz_type = ClinicProfile.BIZ_TYPES[0][0]
                print("%s --> %s"  % (clinic_name, ClinicProfile.BIZ_TYPES[0][0]))

            obj.save()
