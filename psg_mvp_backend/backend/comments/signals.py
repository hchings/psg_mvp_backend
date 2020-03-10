"""
Signals for Comments app.

"""
from annoying.functions import get_object_or_None

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


from .models import Comment

user_model = get_user_model()


@receiver(pre_save, sender=Comment)
def ensure_author_name(sender, instance, **kwargs):
    """
    If the instance has author.uuid, it will auto-fill in the
    correct username from the db.

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    # TODO: need fix
    try:
        author_uuid = instance.author.uuid
        user_obj = get_object_or_None(user_model, uuid=author_uuid)

        if user_obj and user_obj.username:
            instance.author.name = user_obj.username
    except AttributeError:
        pass
