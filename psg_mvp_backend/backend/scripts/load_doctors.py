"""
A simple one-time use hard-coded and interactive script to read doctor data from an csv.
Reason: Djongo's ArrayModelField is bad to use from Django's admin page
        and ListField is not available from the admin page.

To run:
    python manage.py runscript load_doctors

"""
import pandas as pd
from annoying.functions import get_object_or_None
import coloredlogs, logging

from users.models import User
from users.clinics.models import ClinicProfile
from users.doctors.models import DoctorProfile

# Create a logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

# hard-coded info
DEFAULT_PW = '123456'
CSV_FILE_NAME = '../doctors.csv'

SEPARATORS = ['▪', '\n']
CERTIFICATE_TERMS = ['證書']


def run():
    # read in csv
    df = pd.read_csv(CSV_FILE_NAME, header=0)
    # clear up column name
    df.columns = [item.strip() for item in df.columns]

    print(df.head())

    for key, row in df.iterrows():
        # -----------------------------------------------------
        # 1. get the doctor object, if none, create a new one.
        # -----------------------------------------------------
        doctor_name = str(row['doctor name'])
        doctor_user_obj = get_object_or_None(User,
                                             username=doctor_name,
                                             user_type='doctor')

        # check clinic doctor loaded
        clinic_name = str(row['clinic name'])
        clinic_profile = get_object_or_None(ClinicProfile,
                                            display_name=clinic_name)
        if clinic_profile:
            all_doctors_loaded = clinic_profile.all_doctors_loaded
        else:
            all_doctors_loaded = False

        if not doctor_user_obj:
            if all_doctors_loaded:
                logger.info("Doctor %s does not exist but skip creating as all doctors loaded."
                            % doctor_name)
                continue
            else:
                accept = input("Accept doctor name '%s'? (y/n)" % doctor_name)
                if not (not accept or accept == 'y' or accept == 'yes'):
                    doctor_name = input("doctor name").strip()
                doctor_user_obj = User(username=doctor_name, password=DEFAULT_PW, user_type='doctor')
                try:
                    doctor_user_obj.save()
                    logger.warning("Doctor %s does not exist, created a new one" % doctor_name)
                    # clinic_name = input("clinic name").strip()
                    # doctor_user_obj = get_object_or_None(ClinicProfile,
                    #                                      display_name=doctor_name,
                    #                                      user_type='doctor')
                except Exception as e:
                    logger.error('Doctor %s not exist. Failed to create a new doctor user: %s'
                                 % (doctor_name, str(e)))
        else:
            logger.info("Doctor %s exists." % doctor_name)

        # get doctor profile, assume unique name
        doctor_profile = get_object_or_None(DoctorProfile,
                                            display_name=doctor_name,
                                            uuid=doctor_user_obj.uuid)

        # skip doctor if has been first-checked
        first_check = doctor_profile.first_check
        if first_check:
            logger.info("Skipping doctor %s" % first_check)
            continue

        # -----------------------------------------------------
        # 2. add clinic name
        # -----------------------------------------------------
        if not doctor_profile.clinic_name:
            logger.info("No clinic name found.")
            accept = input("Accept clinic name '%s'? (y/n)" % clinic_name)

            if not (not accept or accept == 'y' or accept == 'yes'):
                clinic_profile = clinic_name = None
                while not clinic_profile:
                    clinic_name = input("clinic name").strip()

                    if clinic_name == 'q' or clinic_name == 'quit':
                        logger.info("Skip entering clinic name")
                        break
                    # check if the clinic exist
                    clinic_profile = get_object_or_None(ClinicProfile,
                                                        display_name=clinic_name)
                    if not clinic_profile:
                        logger.error("Clinic %s does not exist! re-enter clinic name or type 'q' to quit"
                                     % clinic_name)
            else:
                logging.info("Clinic name accepted.")

            if clinic_name:
                doctor_profile.clinic_name = clinic_name
                try:
                    doctor_profile.save()
                    logger.info("Clinic name %s saved (clinic_uuid=%s)."
                                % (clinic_name, doctor_profile.clinic_uuid))
                except Exception as e:
                    logger.error("Doctor profile failed to save clinic name %s: %s"
                                 % (clinic_name, str(e)))

        # -----------------------------------------------------
        # 3. add position info
        # -----------------------------------------------------

        # add title
        if not doctor_profile.position:
            position = str(row['position'])
            position = position.replace(" ", "")
            accept = input("Accept position '%s'? (y/n)" % position)
            if not position or not (not accept or accept == 'y' or accept == 'yes'):
                position = input("position").strip()

            if position:
                doctor_profile.position = position
                doctor_profile.save()
                logger.info("Position %s saved."
                            % position)

        if '中醫' in doctor_profile.position:
            doctor_profile.relevant = False
            doctor_profile.save()

        relevant = doctor_profile.relevant
        if relevant is None:
            relevant = input("Is this doctor (%s) relevant to cosmetic/plastic surgery? (y/n)"
                             % doctor_profile.position)

            if relevant == 'n':
                doctor_profile.relevant = False
            else:
                doctor_profile.relevant = True
            doctor_profile.save()
            logger.info("Set to relevant to %s" % doctor_profile.relevant)

        # TODO: WIP
        # -----------------------------------------------------
        # 4. add experience/degrees/others
        # -----------------------------------------------------
        #
        # degrees, certificates, work_exp, other_exp = \
        #     doctor_profile.degrees, doctor_profile.certificates, \
        #     doctor_profile.work_experience, doctor_profile.other_experience
        #
        # print("--", degrees,certificates,work_exp,other_exp,type(degrees))
        #
        # col_names = ['degrees', 'experience', 'other experience', 'certificates']
        #
        # for name in col_names:
        #     items = str(row[name])
        #     # clear up
        #     items = items.replace("\r", "").replace(",", "\n").replace("▪", "\n")
        #     items = [item for item in items.split("\n") if item]
        #     print(items)
        # for separator in SEPARATORS:
        #     if separator in degrees:
        #         print("%s in !" % separator)

        # doctor_user_obj = get_object_or_None(ClinicProfile,
            #                                      display_name=doctor_name,
            #                                      user_type='doctor')
