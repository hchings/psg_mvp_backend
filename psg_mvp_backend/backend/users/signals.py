"""
Signals for Users app.

"""
import hashlib
import coloredlogs, logging

from annoying.functions import get_object_or_None

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import normalize_newlines

from backend.shared.tasks import update_algolia_record
from users.clinics.serializers import ClinicCardSerializer
from .models import User
from .clinics.models import ClinicProfile
from .doctors.models import DoctorProfile

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


def remove_newlines(text):
    """
    Removes all newline characters from a block of text.
    """
    # First normalize the newlines using Django's nifty utility
    normalized_text = normalize_newlines(text)
    # Then simply remove the newlines like so.
    return normalized_text.replace('\n', ',')


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Using django post_save signals to automatically
    create and save a one-to-one a UserProfile,
    DoctorProfile, or ClinicProfile after a new user
    is created.

    :return: None.
    """
    if created:
        profile = None
        user_id = str(getattr(instance, '_id', ''))
        if instance.user_type == 'doctor':
            profile = DoctorProfile(user_id=user_id,
                                    display_name=instance.username,
                                    uuid=str(instance.uuid))
        elif instance.user_type == 'clinic':
            # TODO: this has to change to many-to-1 mapping w/ User model
            # TODO: username should not affect clinic display_name
            # TODO: user_id in ClinicProfile can be deprecated
            # TODO: when a user claim a ClinicProfile, need to add clinic_uuid to the User object
            profile = ClinicProfile(user_id=user_id,
                                    display_name=instance.username,
                                    uuid=str(instance.uuid))
        # admin
        else:
            return

        if profile:
            profile.save()

@receiver(pre_save, sender=ClinicProfile)
def clinic_profile_store_service_tags_raw(sender, instance, **kwargs):
    """
    Turn services_raw_input field (TextField) of a ClinicProfile into services_raw field (ListField, plain array).
    Need this bcz Djongo does not support users to modify ListField through admin page.

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    # fill in branch id (md5 hash of place id)
    if isinstance(instance, ClinicProfile):
        for branch in instance.branches:
            if branch.place_id and not branch.branch_id:
                try:
                    hash_obj = hashlib.md5(branch.place_id.encode('utf-8'))
                    branch.branch_id = hash_obj.hexdigest()
                except Exception as e:
                    logger.error(e)


@receiver(post_save, sender=ClinicProfile)
def update_algolia_clinic_record(sender, instance, **kwargs):
    serializer = ClinicCardSerializer(instance, indexing_algolia=True)
    update_algolia_record.delay(serializer.data, type="clinic")


@receiver(pre_save, sender=DoctorProfile)
def store_clinic(sender, instance, **kwargs):
    """
    A pre-save signal to fill in the info of Clinic
    in a DoctorProfile

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    # TODO: tmp fix. Djongo's ArrayModelField and ListField
    # TODO: could not have an initial value properly
    instance.degrees = instance.degrees or []
    instance.certificates = instance.certificates or []
    instance.work_exps = instance.work_exps or []
    instance.other_exps = instance.other_exps or []
    instance.services_raw = instance.services_raw or []

    clinic_name = str(getattr(instance, 'clinic_name', ''))
    if clinic_name:
        clinic_profile_obj = get_object_or_None(ClinicProfile, display_name=clinic_name)
        if not clinic_profile_obj:
            instance.clinic_user_id = ''
            pass
        else:
            instance.clinic_uuid = str(getattr(clinic_profile_obj, 'uuid', ''))
