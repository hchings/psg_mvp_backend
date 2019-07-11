"""
Signals for Users app.

"""
from annoying.functions import get_object_or_None

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import normalize_newlines

from .models import User
from .clinics.models import ClinicProfile
from .doctors.models import DoctorProfile
# from .doc_type import ClinicProfileDoc


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
        # user
        if instance.user_type == 'user':
            # profile = UserProfile(user=instance)
            pass
        # doctor
        elif instance.user_type == 'doctor':
            profile = DoctorProfile(user_id=user_id,
                                    display_name=instance.username,
                                    uuid=str(instance.uuid))
        # clinic
        elif instance.user_type == 'clinic':
            profile = ClinicProfile(user_id=user_id,
                                    display_name=instance.username,
                                    uuid=str(instance.uuid))
        # admin
        else:
            return

        if profile:
            profile.save()


@receiver(pre_save, sender=ClinicProfile)
@receiver(pre_save, sender=DoctorProfile)
def clinic_profile_store_service_tags_raw(sender, instance, **kwargs):
    """
    Turn services_raw_input field (TextField) of a ClinicProfile into services_raw field (ListField, plain array).
    Need this bcz Djongo does not support users to modify ListField through admin page.

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    services_raw_input = instance.services_raw_input

    if services_raw_input.strip() == '-':
        instance.services_raw_input = ''
        instance.services_raw = []
    elif services_raw_input:
        services_raw_input = remove_newlines(services_raw_input)
        services_raw_input.replace("\n", ",")
        services_raw_input.replace("，", ",")

        instance.services_raw = [item.strip() for item in services_raw_input.split(',') if item.strip()]
    elif instance.services_raw:
        instance.services_raw_input = ', '.join(instance.services_raw)


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
            # TODO: this part should be guarded at frontend.
            # raise AttributeError('Clinic %s not found when creating doctor %s! \
            #                       Please create the corresponding clinic user and profile first.'
            #                      % (clinic_name, instance.display_name))
            instance.clinic_user_id = ''
            pass
        else:
            instance.clinic_uuid = str(getattr(clinic_profile_obj, 'uuid', ''))


@receiver(post_save, sender=ClinicProfile)
def clinic_profile_index_handler(sender, instance, **kwargs):
    """
    Index clinic profile into ElasticSearch on save.

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    instance.indexing()
