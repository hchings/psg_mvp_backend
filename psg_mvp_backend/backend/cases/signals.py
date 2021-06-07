"""
Signals for Cases app.

"""
import shutil
from os import path
from datetime import datetime
import pytz
import coloredlogs, logging
from annoying.functions import get_object_or_None
from elasticsearch import Elasticsearch
# from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search, Q
# from elasticsearch.helpers import bulk
# from elasticsearch_dsl import UpdateByQuery

from django.conf import settings
from django.db.models.signals import post_delete, pre_save, post_init, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned

from users.clinics.models import ClinicProfile
from users.doctors.models import DoctorProfile
from comments.models import Comment
from backend.shared.utils import invalidate_cached_data
from .models import Case, CaseImages
from .doc_type import CaseDoc
from .tasks import send_case_in_review_confirmed, send_case_published_notice

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}],
                   index="cases")

User = get_user_model()


@receiver(post_save, sender=Case)
def fill_in_on_create(sender, instance, created, **kwargs):
    """
    Fill case.author.scp = True to indicate the case
    is scraped if the case is created by users with is_staff == true.

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    # if new obj got created
    if created:
        # Check whether author is staff (i.e., have access to admin site)
        # if yes, mark the case as scraped

        author_name = instance.author.name
        if author_name:
            user = get_object_or_None(User, username=author_name)
            if user and user.is_staff:
                instance.author.scp = True
                instance.save()
        #
        # print("updated a p to ", instance.posted)
        # instance.author_posted = instance.posted

        # send out "your case is in review email"
        if instance.state == 'reviewing':
            # first surgery
            surgeries = instance.surgeries or []
            first_tag = '' if not surgeries else surgeries[0].name
            logger.info('send out case in review notif.')
            send_case_in_review_confirmed.delay(instance.author.uuid,
                                                first_tag,
                                                instance.title,
                                                instance.uuid)

        # print("!! post_save created signal", instance, instance.state)


# TODO: WIP. need more test. need rewrite...
@receiver(pre_save, sender=Case)
def fill_in_data(sender, instance, **kwargs):
    """

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    # TODO: WIP
    # check the first time the case tranferred from 'review' to 'publish' and not scrapped case
    # and send out a notif email
    if (instance.state == 'published' or instance.state == 2) and not instance.author.scp:
        pre_save_instance = get_object_or_None(Case, uuid=instance.uuid)
        if pre_save_instance and \
                (pre_save_instance.state == 'reviewing' or pre_save_instance.state == 1):
            surgeries = instance.surgeries or []
            first_tag = '' if not surgeries else surgeries[0].name
            logger.info('send out case published notif.')
            send_case_published_notice.delay(instance.author.uuid,
                                             first_tag,
                                             instance.title,
                                             instance.uuid)
            # print("---send out published signal")

    # sanity check on status
    if not instance.state:
        instance.state = 'draft'

    # assign failed case
    # TODO: TMP, bad
    if instance.rating == 1:
        instance.failed = True

    # author

    # clinic
    if instance.clinic and instance.clinic.display_name:
        try:
            clinic = get_object_or_None(ClinicProfile, display_name=instance.clinic.display_name)
        except MultipleObjectsReturned:
            clinic = ClinicProfile.objects.filter(display_name=instance.clinic.display_name).first()
            logger.warning("Found duplicated clinic profile: %s" % clinic)
        # has corresponding clinic
        if clinic:
            # fix potential djongo issues
            if not clinic.services:
                clinic.services = []

            instance.clinic.uuid = clinic.uuid
            # fill in branch place id
            head_quarter = None
            matched_branch = None
            if clinic.branches:
                for branch in clinic.branches:
                    # print(branch, branch.branch_name, branch.is_head_quarter, instance.clinic.branch_name)
                    if branch.is_head_quarter:
                        head_quarter = branch
                        if not instance.clinic.branch_name:
                            matched_branch = head_quarter
                            break
                    if branch.branch_name == instance.clinic.branch_name:
                        matched_branch = branch
                        break

                # fix error data
                # TODO: clean up data here is kinda bad
                if not head_quarter and len(clinic.branches) == 1:
                    clinic.branches[0].is_head_quarter = True
                    try:
                        clinic.save()
                    except:
                        logger.info('[fill in data] Clinic save setting HQ failed %s' % clinic)

                if matched_branch:
                    instance.clinic.place_id = matched_branch.place_id or ''
                    instance.clinic.branch_name = matched_branch.branch_name
                    logger.info("[Fill in case data] Found matched branch name %s of clinic %s for case %s" %
                                (instance.clinic.branch_name,
                                 instance.clinic.display_name,
                                 instance.uuid))
                elif head_quarter:
                    # if branch unexist, notify, change to head quarter
                    instance.clinic.place_id = head_quarter.place_id or ''
                    logger.warning("[Fill in case data] Branch %s of clinic %s for case %s is not found,"
                                   " use head quarter." %
                                   (instance.clinic.branch_name,
                                    instance.clinic.display_name,
                                    instance.uuid))
            # Link to DoctorProfile if any. TODO: double check
            if instance.clinic.doctor_name:
                try:
                    doctor_profile = get_object_or_None(DoctorProfile,
                                                        clinic_uuid=clinic.uuid,
                                                        display_name=instance.clinic.doctor_name)
                except MultipleObjectsReturned:
                    doctor_profile = DoctorProfile.objects.filter(clinic_uuid=clinic.uuid,
                                                                  display_name=instance.clinic.doctor_name).first()
                    logger.warning("Found duplicated doctor: %s" % doctor_profile)
                if doctor_profile:
                    logger.info("[Fill in case data] Found matched doctor profile for doctor %s for case %s" %
                                (doctor_profile.display_name,
                                 instance.uuid))
                    instance.clinic.doctor_profile_id = doctor_profile._id or ''
                else:
                    # clear obsolete doctor_profile_id
                    instance.clinic.doctor_profile_id = ''

        else:
            instance.clinic.uuid = ''
            instance.clinic.place_id = ''
            logger.error("[Fill in case data] Clinic %s of case %s not found!" %
                         (instance.clinic.display_name,
                          instance.uuid))
        # if clinic name exist, fill in uuid, else notify and nullify uuid

    # ------ [IMPORTANT !!] Create/Update ES --------
    # check ES record, only if it's a published case
    try:
        query = Q({"match": {"id": str(instance.uuid)}})
        s = CaseDoc.search(index='cases').query(query)
        if instance.state == 'published' or instance.state == 2:
            if s.count() == 0:
                logger.info('Indexed case %s into ES.' % instance.uuid)
                instance.indexing()
            else:
                # has record, delete and re-index
                response = s.delete()
                logger.info("Deleted document of case %s in ES: %s for reindexing" % (instance.uuid,
                                                                                      response))
                instance.indexing()
        else:
            # remove the ES record is state change
            if s.count() > 0:
                response = s.delete()
                logger.info("Deleted document of case %s in ES: %s" % (instance.uuid,
                                                                       response))
    # NotFoundError
    except Exception as e:
        # prevent ES crashes
        logger.error("[Error write case signal]: %s" % str(e))
        pass

    # check for migration
    # This is a patch for djongo's Listfield.
    # it sucks at providing the right default for old records.
    if instance.pain_points is None:
        instance.pain_points = []  # provide a default

    # update author_posted field
    try:
        request_user = instance._request_user

        if request_user and str(request_user.uuid) == str(instance.author.uuid):
            instance.author_posted = datetime.now(pytz.utc)
    except Exception as e:
        pass

    # regardless of scp or not

    # TODO: update searchable fields
    # ubq = UpdateByQuery(index="cases").using(es).query("match", title="old title").script(
    #     source="ctx._source.title='new title'")
    # result = bulk(
    #     client=es,
    #     actions=(instance.indexing())
    # )
    # logger.info("updated case %s in ES: %s" % (instance.uuid, result))

# TODO: this got called four times on a save
# TODO: this is bad perf.
# bug: change img, thumb not change
@receiver(post_save, sender=Case)
def case_health_check(sender, instance, **kwargs):
    # check thumbnail
    try:
        # print("------post save")
        if instance.af_img:
            thumb_path = instance.af_img_thumb.path
            # if not path.exists(thumb_path):
            instance.af_img_thumb.generate(force=True)
            # logger.info("[case singal post save %s]: regen thumb %s" % (instance.uuid, instance.af_img_thumb))

        if instance.bf_img:
            thumb_path = instance.bf_img_thumb.path
            # if not path.exists(thumb_path):
            instance.bf_img_thumb.generate(force=True)
            # logger.info("[case singal post save %s]: regen thumb %s" % (instance.uuid, instance.bf_img_thumb))
    except Exception as e:
        logger.error("[case singal Error post save %s]: %s" % (instance.uuid, str(e)))

    ############################
    #    Cache Invalidation
    ############################

    # invalidate case detail cache -- both edit and non edit mode
    invalidate_cached_data('case_detail_%s' % instance.uuid)
    invalidate_cached_data('case_detail_edit_%s' % instance.uuid)

    # invalid case search cache only if the status is published,
    # otherwise no affect.
    if instance.state == 'published':
        # delete all case search keys
        invalidate_cached_data('', True)


@receiver(post_delete, sender=Case)
def delete_media(sender, instance, **kwargs):
    """
    1. Clean up the media of a Case after it is deleted.
    This assume files are NOT readonly.

    2. Clean up all comments

    :return: None.
    """
    # 1. delte images in other model
    # delete any photos in other model -- CaseImages
    # Note the difference of calling delete() in bulk and on each obj
    # Doc: https://docs.djangoproject.com/en/3.0/topics/db/queries/
    objs = CaseImages.objects.filter(case_uuid=instance.uuid)
    for obj in objs:
        obj.delete()

    # 2.1 delete its whole directory
    dir_path = 'cases/case_' + str(instance.uuid) + '/'
    try:
        shutil.rmtree(path.join(settings.MEDIA_ROOT, dir_path))
        logging.info('Deleted: ' + path.join(settings.MEDIA_ROOT, dir_path))
    except FileNotFoundError:
        logging.error('Post %s\'s media no need cleaning.' % str(instance.uuid))

    # 2.2 delete folder in CACHE/ TODO: check
    dir_path = 'CACHE/images/cases/case_' + str(instance.uuid) + '/'
    try:
        shutil.rmtree(path.join(settings.MEDIA_ROOT, dir_path))
        logging.info('Deleted: ' + path.join(settings.MEDIA_ROOT, dir_path))
    except FileNotFoundError:
        logging.error('Post %s\'s cache media no need cleaning. %s'
                      % (str(instance.uuid), path.join(settings.MEDIA_ROOT, dir_path)))

    # 3. delete reference in ES
    s = Search(index="cases").using(es).query("match", id=str(instance.uuid))
    res = s.delete()
    logger.info("Removed %s ES record of case %s" % (res['deleted'], instance.uuid))

    # 4. delete comments
    comment_objs = Comment.objects.filter(case_id=instance.uuid)
    comment_objs.delete()  # instantly delete
