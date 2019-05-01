"""
Signals for Users app.

"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User
from .clinics.models import ClinicProfile


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
            pass
            # profile = UserProfile(user=instance)
        # doctor
        elif instance.user_type == 'doctor':
            pass
            # profile = DoctorProfile(user=instance)
        # clinic
        elif instance.user_type == 'clinic':
            profile = ClinicProfile(user_id=user_id, display_name=instance.username, uuid=str(instance.uuid))
        # admin
        else:
            return

        if profile:
            profile.save()
