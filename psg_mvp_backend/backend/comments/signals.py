"""
Signals for Comments app.

"""
from annoying.functions import get_object_or_None
from actstream.models import Action

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from backend.shared.utils import invalidate_cached_data

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

    ############################
    #    Cache Invalidation
    ############################

    # invalidate case detail cache -- only non edit mode
    invalidate_cached_data('case_detail_%s' % instance.case_id)
    # delete all case search keys
    invalidate_cached_data('', True)


@receiver(post_save, sender=Action)
@receiver(post_delete, sender=Action)
def action_update(sender, instance, **kwargs):
    ############################
    #    Cache Invalidation
    ############################

    # invalidate case detail cache -- only non edit mode
    # print("action object", instance.action_object, type(instance.action_object))
    invalidate_cached_data('case_detail_%s' % instance.action_object.uuid)
    # invalidate_cached_data('case_detail_%s' % instance.action_object.case_id)
    # delete all case search keys
    invalidate_cached_data('', True)
