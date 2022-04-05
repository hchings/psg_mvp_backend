import shutil
from os import path

import coloredlogs, logging
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from backend.shared.tasks import update_algolia_record

from .models import Review
from .serializers import ReviewSerializer


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

# TODO: WIP
@receiver(post_save, sender=Review)
def fill_in_on_create(sender, instance, created, **kwargs):
    if instance.state == 'published':

        serializer = ReviewSerializer(instance,
                                      indexing_algolia=True)
        # update case in Algolia
        update_algolia_record.delay(serializer.data, type="review")



@receiver(post_delete, sender=Review)
def delete_media(sender, instance, **kwargs):
    """
    1. Clean up the media of a Case after it is deleted.
    This assume files are NOT readonly.

    2. Clean up all comments

    :return: None.
    """
    print("post delete review")
    # 1 delete its whole directory
    dir_path = 'reviews/review_' + str(instance.uuid) + '/'
    try:
        shutil.rmtree(path.join(settings.MEDIA_ROOT, dir_path))
        print("try to delete dir %s", path.join(settings.MEDIA_ROOT, dir_path))
        logging.info('Deleted: ' + path.join(settings.MEDIA_ROOT, dir_path))
    except FileNotFoundError as e:
        print("Error!!!!", str(e))
        logging.error('Post review %s\'s media no need cleaning.' % str(instance.uuid))

    # 2 delete folder in CACHE/ TODO: check
    dir_path = 'CACHE/images/reviews/review_' + str(instance.uuid) + '/'
    try:
        shutil.rmtree(path.join(settings.MEDIA_ROOT, dir_path))
        logging.info('Deleted: ' + path.join(settings.MEDIA_ROOT, dir_path))
    except FileNotFoundError:
        logging.error('Post review %s\'s cache media no need cleaning. %s'
                      % (str(instance.uuid), path.join(settings.MEDIA_ROOT, dir_path)))
