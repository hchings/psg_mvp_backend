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
from users.doctors.models import BackgroundItem
import re

# Create a logger j
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

# hard-coded info
DEFAULT_PW = '123456'
CSV_FILE_NAME = '../doctors.csv'

SEPARATORS = ['▪', '\n', '\r', ',', '•']
CERTIFICATE_TERMS = ['證書']
TEST_DOCTOR_ACCT_NAME = 'TEST_DOCTOR'
TEST_DOCTOR_CLINIC_NAME = '悠美診所'
TEST_DOCTOR_POSITION = '院長'

# TODO: clean up WARNING messages
# TODO: run with python manage.py runscript load_doctors |& tee output.txt

def run():
    # read in csv
    df = pd.read_csv(CSV_FILE_NAME, header=0)
    # clear up column name
    df.columns = [item.strip() for item in df.columns]

    print(df.head())

    def dataCleanUp(raw_data_input):
        raw_data_input = raw_data_input.replace(',', '\n')
        raw_data_input = re.sub("[：, ,＿,．,-]", "", raw_data_input)
        clean_data = re.sub("[▪,\r,\,,•,\t,■,。,．,‧,，,◦,►,●,*,￭,\u3000,»,｜,✿]", "\n", raw_data_input)
        return clean_data

    # Control to run in test mode or not. Test mode will create a TEST_DOCTOR and only log without updating any record
    while True:
        test_control = input("Run in test mode (pure logging, no record will be updated)? (y/n) ")
        if test_control == 'n':
            test_control_confirm = input("Confirm NOT to run in test mode? Records WILL be updated (y/n) ")
        else:
            test_control_confirm = input("Confirm to run in test mode? (y/n) ")

        if test_control_confirm == 'y':
            break
        else:
            continue

    # Control to run in override mode or not. Override mode will override existing records without checking.
    while True:
        override_control = input("Run in override mode (override existing records if exist)? (y/n) ")
        if override_control == 'n':
            override_control_confirm = input("Confirm NOT to run in override mode? (y/n) ")
        else:
            override_control_confirm = \
                input("Confirm to run in override mode? Existing records WILL be overridden (y/n) ")
        if override_control_confirm == 'y':
            break
        else:
            continue

    # Control to run in no-parsing mode or not. No parsing mode will not parse the input records except splitting by \n

    while True:
        no_parsing_control = input("Run in no-parsing mode (not parse the input records except splitting)? (y/n) ")
        if no_parsing_control == 'y':
            no_parsing_control_confirm = input("Confirm to run in no-parsing mode? Records will NOT be parsed (y/n) ")
        else:
            no_parsing_control_confirm = input("Confirm to run in parsing mode? Records WILL be parsed (y/n) ")

        if no_parsing_control_confirm == 'y':
            break
        else:
            continue

    if override_control == 'n':
        override_mode = False
    else:
        override_mode = True

    if test_control == 'n':
        test_mode = False
    else:
        test_mode = True

    if no_parsing_control == 'y':
        no_parsing_mode = True
    else:
        no_parsing_mode = False

    if test_mode:
        doctor_name = TEST_DOCTOR_ACCT_NAME
        doctor_user_obj = get_object_or_None(User,
                                             username=doctor_name,
                                             user_type='doctor')
        if not doctor_user_obj:
            doctor_user_obj = User(username=doctor_name, password=DEFAULT_PW, user_type='doctor')
            try:
                doctor_user_obj.save()
                logger.warning("Running in test mode with no %s. Creating Doctor record for %s"
                               % (doctor_name, doctor_name))
            except Exception as e:
                logger.error("Doctor %s: Doctor profile does not exist. Failed to create a new one. Exiting. Error: %s"
                             % (doctor_name, str(e)))
                exit()
        else:
            logger.info("Running in test mode with %s profile already created." % doctor_name)

    for key, row in df.iterrows():
        # -----------------------------------------------------
        # 1. get the doctor object, if none, create a new one.
        # -----------------------------------------------------
        if pd.isna(row['doctor name']):
            logger.info("No doctor name exist on row. Skipping this row")
            continue

        doctor_name = str(row['doctor name'])
        doctor_name = re.sub(r'\W+', '', doctor_name)

        doctor_user_obj = get_object_or_None(User,
                                             username=doctor_name,
                                             user_type='doctor')

        # check whether clinic record exists and whether all doctors have been loaded
        if pd.isna(row['clinic name']):
            logger.warning("Doctor %s: No clinic name entry. Skipping this record" % doctor_name)
            continue

        clinic_name = str(row['clinic name'])
        clinic_profile = get_object_or_None(ClinicProfile,
                                            display_name=clinic_name)
        if not clinic_profile:
            logger.warning("Doctor %s: Clinic record %s does not exist"
                           % (doctor_name, clinic_name))
            all_doctors_loaded = False
        else:
            all_doctors_loaded = clinic_profile.all_doctors_loaded

        if not doctor_user_obj:
            if all_doctors_loaded:
                logger.info("Doctor %s: Doctor does not exist but skip creating as all doctors loaded for clinic %s."
                            % (doctor_name, clinic_name))
                continue
            else:
                doctor_user_obj = User(username=doctor_name, password=DEFAULT_PW, user_type='doctor')
                try:
                    if not test_mode:
                        doctor_user_obj.save()
                    logger.warning("Doctor %s: Doctor profile does not exist, created a new one" % doctor_name)
                except Exception as e:
                    logger.error("Doctor %s: Doctor profile does not exist. Failed to create a new one. Error: %s"
                                 % (doctor_name, str(e)))
                    continue
        else:
            logger.info("Doctor %s: Doctor profile already exists." % doctor_name)

        if not test_mode:
            # get doctor profile, assume unique name
            doctor_profile = get_object_or_None(DoctorProfile,
                                                display_name=doctor_name,
                                                uuid=doctor_user_obj.uuid)

            if not doctor_profile:
                logger.error("Doctor %s: Failed to get doctor profile. Skipping remaining load for this doctor."
                               % doctor_name)
                continue

            # skip doctor if has been first-checked
            first_check = doctor_profile.first_check
            if first_check:
                logger.info("Doctor %s: Skipping doctor as record has been checked" % doctor_name)
                continue

        else:
            doctor_user_obj = get_object_or_None(User,
                                                 username=TEST_DOCTOR_ACCT_NAME,
                                                 user_type='doctor')

            doctor_profile = get_object_or_None(DoctorProfile,
                                                display_name=TEST_DOCTOR_ACCT_NAME,
                                                uuid=doctor_user_obj.uuid)
            if not doctor_profile:
                logger.error("Doctor %s: Failed to get TEST_DOCTOR profile. Exiting."
                               % doctor_name)
                exit()

            doctor_profile.clinic_name = TEST_DOCTOR_CLINIC_NAME
            doctor_profile.position = TEST_DOCTOR_POSITION

        # -----------------------------------------------------
        # 2. add clinic name
        # -----------------------------------------------------
        if (not doctor_profile.clinic_name) or (doctor_profile.clinic_name and override_mode):
            if not doctor_profile.clinic_name:
                logger.info("Doctor %s: No clinic name found on doctor profile." % doctor_name)
            else:
                logger.info("Doctor %s: Clinic name %s exist. Enter override mode."
                            % (doctor_name, doctor_profile.clinic_name))
            if clinic_name:
                doctor_profile.clinic_name = clinic_name
                try:
                    if not test_mode:
                        doctor_profile.save()
                    logger.info("Doctor %s: Clinic name %s saved (clinic_uuid=%s)."
                                % (doctor_name, clinic_name, doctor_profile.clinic_uuid))
                except Exception as e:
                    logger.error("Doctor %s: Profile failed to save clinic name %s. Error: %s"
                                 % (doctor_name, clinic_name, str(e)))
        else:
            logger.info("Doctor %s: Clinic name %s already exist. Skip clinic name (not running in override mode)."
                        % (doctor_name, doctor_profile.clinic_name))

        # -----------------------------------------------------
        # 3. add position info
        # -----------------------------------------------------

        # add position
        if (not doctor_profile.position) or (doctor_profile.position and override_mode):
            if not doctor_profile.position:
                logger.info("Doctor %s: No position found on doctor profile." % doctor_name)
            else:
                logger.info("Doctor %s: Position %s exist. Enter override mode."
                            % (doctor_name, doctor_profile.position))
            if pd.isna(row['position']):
                logger.warning("Doctor %s: No position entry exist for this doctor" % doctor_name)
            else:
                position_raw = str(row['position'])
                position_clean = re.sub(r'\W+', '', position_raw)
                if position_clean:
                    doctor_profile.position = position_clean
                    if '中醫' in doctor_profile.position:
                        doctor_profile.relevant = False
                    try:
                        if not test_mode:
                            doctor_profile.save()
                        logger.info("Doctor %s: Position %s saved."
                                    % (doctor_name, position_clean))
                    except Exception as e:
                        logger.error("Doctor %s: Profile failed to save position %s. Error: %s"
                                     % (doctor_name, position_clean, str(e)))
        else:
            logger.info("Doctor %s: Position %s already exist. Skip position (not running in override mode)."
                        % (doctor_name, doctor_profile.position))

        # Removed "relevant" check during loading.

        # -----------------------------------------------------
        # 4. add degrees
        # -----------------------------------------------------
        if pd.isna(row['degrees']):
            logger.info("Doctor %s: No degree entry exist for this doctor" % doctor_name)
            if override_mode and doctor_profile.degrees:
                logger.warning("Doctor %s: Override mode activated, override degree record to empty. "
                               "Existing degrees %s" % (doctor_name, doctor_profile.degrees))
                doctor_profile.degrees = []
                try:
                    if not test_mode:
                        doctor_profile.save()
                    logger.info("Doctor %s: Degree info overridden to empty. New degree info: %s"
                                % (doctor_name, doctor_profile.degrees))

                except Exception as e:
                    logger.error("Doctor %s: Doctor profile degree failed to set to empty. Error: %s"
                                 % (doctor_name, str(e)))
        else:
            degrees_raw = str(row['degrees'])
            if not no_parsing_mode:
                degrees_clean = dataCleanUp(degrees_raw)
                degree_name_list = [item.replace(',', '') for item in degrees_clean.split('\n') if item]
            else:
                degrees_clean = degrees_raw.replace('\r', '\n')
                degree_name_list = [item for item in degrees_clean.split('\n') if item]

            if not doctor_profile.degrees:
                doctor_profile.degrees = []

            if doctor_profile.degrees and override_mode:
                logger.info("Doctor %s: Degrees exist. Enter override mode. Existing degrees: %s"
                            % (doctor_name, doctor_profile.degrees))
                doctor_profile.degrees = []

            items = [_.item for _ in doctor_profile.degrees]

            for degree_name in degree_name_list:
                if degree_name in items:
                    logging.info("Doctor %s: Degree %s exists." % (doctor_name, degree_name))
                else:
                    degree_background_item = BackgroundItem(item=degree_name)
                    doctor_profile.degrees.append(degree_background_item)

            try:
                if not test_mode:
                    doctor_profile.save()
                logger.info("Doctor %s: Degree info saved. Details: %s" % (doctor_name, doctor_profile.degrees))

            except Exception as e:
                logger.error("Doctor %s: Doctor profile failed to save for degree info. Error: %s"
                             % (doctor_name, str(e)))

        # -----------------------------------------------------
        # 5. add experiences
        # -----------------------------------------------------

        if pd.isna(row['experience']):
            logger.info("Doctor %s: No experience entry exist for this doctor" % doctor_name)
            if override_mode and doctor_profile.work_exps:
                logger.warning("Doctor %s: Override mode activated, override experience record to empty. "
                               "Existing experiences %s" % (doctor_name, doctor_profile.work_exps))
                doctor_profile.work_exps = []
                try:
                    if not test_mode:
                        doctor_profile.save()
                    logger.info("Doctor %s: Experience info overridden to empty. New experience info: %s"
                                % (doctor_name, doctor_profile.work_exps))

                except Exception as e:
                    logger.error("Doctor %s: Doctor profile experience info failed to set to empty. Error: %s"
                                 % (doctor_name, str(e)))
        else:
            experiences_raw = str(row['experience'])
            if not no_parsing_mode:
                experiences_clean = dataCleanUp(experiences_raw)
                experiences_entry_list = [item.replace(',', '') for item in experiences_clean.split('\n') if item]
            else:
                experiences_clean = experiences_raw.replace('\r', '\n')
                experiences_entry_list = [item for item in experiences_clean.split('\n') if item]

            if not doctor_profile.work_exps:
                doctor_profile.work_exps = []

            if doctor_profile.work_exps and override_mode:
                logger.info("Doctor %s: Experiences exist. Enter override mode. Existing experiences: %s"
                            % (doctor_name, doctor_profile.work_exps))
                doctor_profile.work_exps = []

            items = [_.item for _ in doctor_profile.work_exps]

            for experiences_entry in experiences_entry_list:
                if experiences_entry in items:
                    logging.info("Doctor %s: Experience %s exists." % (doctor_name, experiences_entry))
                else:
                    experiences_entry_background_item = BackgroundItem(item=experiences_entry)
                    doctor_profile.work_exps.append(experiences_entry_background_item)

            try:
                if not test_mode:
                    doctor_profile.save()
                logger.info("Doctor %s: Experience info saved. Details: %s" % (doctor_name, doctor_profile.work_exps))
            except Exception as e:
                logger.error("Doctor %s: Doctor profile failed to save for experience info. Error: %s"
                             % (doctor_name, str(e)))


        # -----------------------------------------------------
        # 6. add other experiences
        # -----------------------------------------------------

        if pd.isna(row['other experience']):
            logger.info("Doctor %s: No other experience entry exist for this doctor" % doctor_name)
            if override_mode and doctor_profile.other_exps:
                logger.warning("Doctor %s: Override mode activated, override other experience record to empty. "
                               "Existing other experiences %s" % (doctor_name, doctor_profile.other_exps))
                doctor_profile.other_exps = []
                try:
                    if not test_mode:
                        doctor_profile.save()
                    logger.info("Doctor %s: Other experience info overridden to empty. New experience info: %s"
                                % (doctor_name, doctor_profile.other_exps))

                except Exception as e:
                    logger.error("Doctor %s: Doctor profile other experience info failed to set to empty. Error: %s"
                                 % (doctor_name, str(e)))
        else:
            other_experiences_raw = str(row['other experience'])
            if not no_parsing_mode:
                other_experiences_clean = dataCleanUp(other_experiences_raw)
                other_experiences_entry_list = [item.replace(',', '') for item in
                                                other_experiences_clean.split('\n') if item]
            else:
                other_experiences_clean = other_experiences_raw.replace('\r', '\n')
                other_experiences_entry_list = [item for item in
                                                other_experiences_clean.split('\n') if item]

            if not doctor_profile.other_exps:
                doctor_profile.other_exps = []

            if doctor_profile.other_exps and override_mode:
                logger.info("Doctor %s: Other experiences exist. Enter override mode. Existing other experiences: %s"
                            % (doctor_name, doctor_profile.other_exps))
                doctor_profile.other_exps = []

            items = [_.item for _ in doctor_profile.other_exps]

            for other_experiences_entry in other_experiences_entry_list:
                if other_experiences_entry in items:
                    logging.info("Doctor %s: Other experience %s exists." % (doctor_name, other_experiences_entry))
                else:
                    other_experiences_entry_background_item = BackgroundItem(item=other_experiences_entry)
                    doctor_profile.other_exps.append(other_experiences_entry_background_item)

            try:
                if not test_mode:
                    doctor_profile.save()
                logger.info("Doctor %s: Other experience info saved. Details: %s"
                            % (doctor_name, doctor_profile.other_exps))
            except Exception as e:
                logger.error("Doctor %s: Doctor profile failed to save for other experience info. Error: %s"
                             % (doctor_name, str(e)))


        # -----------------------------------------------------
        # 7. add certificates
        # -----------------------------------------------------

        if pd.isna(row['certificates']):
            logger.info("Doctor %s: No certificate entry exist for this doctor" % doctor_name)
            if override_mode and doctor_profile.certificates:
                logger.warning("Doctor %s: Override mode activated, override certificate record to empty. "
                               "Existing certificates %s" % (doctor_name, doctor_profile.certificates))
                doctor_profile.certificates = []
                try:
                    if not test_mode:
                        doctor_profile.save()
                    logger.info("Doctor %s: certificate info overridden to empty. New certificate info: %s"
                                % (doctor_name, doctor_profile.certificates))

                except Exception as e:
                    logger.error("Doctor %s: Doctor profile certificate failed to set to empty. Error: %s"
                                 % (doctor_name, str(e)))
        else:
            certificates_raw = str(row['certificates'])
            if not no_parsing_mode:
                certificates_clean = dataCleanUp(certificates_raw)
                certificates_list = [item.replace(',', '') for item in certificates_clean.split('\n') if item]
            else:
                certificates_clean = certificates_raw.replace('\r', '\n')
                certificates_list = [item for item in certificates_clean.split('\n') if item]

            if not doctor_profile.certificates:
                doctor_profile.certificates = []

            if doctor_profile.certificates and override_mode:
                logger.info("Doctor %s: Certificates exist. Enter override mode. Existing certificates: %s"
                            % (doctor_name, doctor_profile.certificates))
                doctor_profile.certificates = []

            items = [_.item for _ in doctor_profile.certificates]

            for certificate_name in certificates_list:
                if certificate_name in items:
                    logging.info("Doctor %s: Certificate %s exists." % (doctor_name, certificate_name))
                else:
                    certificate_background_item = BackgroundItem(item=certificate_name)
                    doctor_profile.certificates.append(certificate_background_item)

            try:
                if not test_mode:
                    doctor_profile.save()
                logger.info("Doctor %s: Certificates info saved. Details: %s"
                            % (doctor_name, doctor_profile.certificates))
            except Exception as e:
                logger.error("Doctor %s: Doctor profile failed to save for certificates info. Error: %s"
                             % (doctor_name, str(e)))


        # -----------------------------------------------------
        # 8. add professions
        # -----------------------------------------------------

        if pd.isna(row['professionals']):
            logger.info("Doctor %s: No profession entry exist for this doctor" % doctor_name)
            if override_mode and doctor_profile.services_raw:
                logger.warning("Doctor %s: Override mode activated, override services record to empty. "
                               "Existing services %s" % (doctor_name, doctor_profile.services_raw))
                doctor_profile.services_raw = []
                try:
                    if not test_mode:
                        doctor_profile.services_raw_input = ""
                        doctor_profile.save()
                    logger.info("Doctor %s: Degree info overridden to empty. New services info: %s"
                                    % (doctor_name, doctor_profile.services_raw))

                except Exception as e:
                    logger.error("Doctor %s: Doctor profile services failed to set to empty. Error: %s"
                                 % (doctor_name, str(e)))
        else:
            services_raw = str(row['professionals'])
            if not no_parsing_mode:
                services_clean = dataCleanUp(services_raw)
                services_list = [item.replace(',', '') for item in services_clean.split('\n') if item]
            else:
                services_clean = services_raw.replace('\r', '\n')
                services_list = [item for item in services_clean.split('\n') if item]

            if not doctor_profile.services_raw:
                doctor_profile.services_raw = []

            if doctor_profile.services_raw and override_mode:
                logger.info("Doctor %s: Services exist. Enter override mode. Existing services: %s"
                            % (doctor_name, doctor_profile.services_raw))
                doctor_profile.services_raw = []

            for service_name in services_list:
                if service_name in doctor_profile.services_raw:
                    logging.info("Doctor %s: Service %s exists." % (doctor_name, service_name))
                else:
                    doctor_profile.services_raw.append(service_name)

            try:
                if not test_mode:
                    doctor_profile.services_raw_input = ', '.join(doctor_profile.services_raw)
                    doctor_profile.save()
                logger.info("Doctor %s: Services info saved. Details: %s"
                            % (doctor_name, doctor_profile.services_raw))
            except Exception as e:
                logger.error("Doctor %s: Doctor profile failed to save for services info. Error: %s"
                             % (doctor_name, str(e)))

