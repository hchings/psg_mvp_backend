"""
Signals for Cases app.

"""
import shutil, os
import coloredlogs, logging
from annoying.functions import get_object_or_None
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
# from elasticsearch.helpers import bulk
# from elasticsearch_dsl import UpdateByQuery

from django.conf import settings
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from users.clinics.models import ClinicProfile
from .models import Case, CaseImages

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}],
                   index="cases")


# TODO: WIP. need more test.
@receiver(pre_save, sender=Case)
def fill_in_data(sender, instance, **kwargs):
    # status
    # if not instance.state:
    #     instance.state = 'draft'

    # author

    # clinic
    if instance.clinic.display_name:
        clinic = get_object_or_None(ClinicProfile, display_name=instance.clinic.display_name)
        if clinic:
            instance.clinic.uuid = clinic.uuid
            # fill in branch place id
            head_quarter = None
            matched_branch = None
            if clinic.branches:
                for branch in clinic.branches:
                    print(branch, branch.branch_name, branch.is_head_quarter, instance.clinic.branch_name)
                    if branch.is_head_quarter:
                        head_quarter = branch
                        if not instance.clinic.branch_name:
                            matched_branch = head_quarter
                            break
                    if branch.branch_name == instance.clinic.branch_name:
                        matched_branch = branch
                        break
                if matched_branch:
                    instance.clinic.place_id = matched_branch.place_id or ''
                    instance.clinic.branch_name = matched_branch.branch_name
                    logger.info("[Fill in case data] Found matched branch name %s of clinic %s for case %s" %
                                (instance.clinic.branch_name,
                                 instance.clinic.display_name,
                                 instance.uuid))
                else:
                    # if branch unexist, notify, change to head quarter
                    instance.clinic.place_id = head_quarter.place_id or ''
                    logger.warning("[Fill in case data] Branch %s of clinic %s for case %s is not found,"
                                   " use head quarter." %
                                   (instance.clinic.branch_name,
                                    instance.clinic.display_name,
                                    instance.uuid))
        else:
            instance.clinic.uuid = ''
            instance.clinic.place_id = ''
            logger.error("[Fill in case data] Clinic %s of case %s not found!" %
                         (instance.clinic.display_name,
                          instance.uuid))
        # if clinic name exist, fill in uuid, else notify and nullify uuid

    # ------ [IMPORTANT !!] Create/Update ES --------
    # ubq = UpdateByQuery(index="cases").using(es).query("match", title="old title").script(
    #     source="ctx._source.title='new title'")
    # result = bulk(
    #     client=es,
    #     actions=(instance.indexing())
    # )
    # logger.info("updated case %s in ES: %s" % (instance.uuid, result))


@receiver(post_delete, sender=Case)
def delete_media(sender, instance, **kwargs):
    """
    Clean up the media of a Case after it is deleted.
    This assume files are NOT readonly.

    :return: None.
    """
    # 1. delte images in other model
    # delete any photos in other model -- CaseImages
    # Note the difference of calling delete() in bulk and on each obj
    # Doc: https://docs.djangoproject.com/en/3.0/topics/db/queries/
    objs = CaseImages.objects.filter(case_uuid=instance.uuid)
    for obj in objs:
        obj.delete()

    # 2. delete its whole directory
    dir_path = 'cases/case_' + str(instance.uuid) + '/'
    try:
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, dir_path))
        logging.info('Deleted: ' + os.path.join(settings.MEDIA_ROOT, dir_path))
    except FileNotFoundError:
        logging.error('Post %s\'s media no need cleaning.' % str(instance.uuid))

    # 3. delete reference in ES
    s = Search(index="cases").using(es).query("match", id=str(instance.uuid))
    res = s.delete()
    logger.info("Removed %s ES record of case %s" % (res['deleted'], instance.uuid))
