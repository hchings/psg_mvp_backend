"""
Shared Celery tasks

"""

from algoliasearch.search_client import SearchClient
from annoying.functions import get_object_or_None
import coloredlogs, logging

from backend.settings import ALGOLIA_APP_ID, ALGOLIA_SECRET, \
    ALGOLIA_CASE_INDEX, ALGOLIA_CLINIC_INDEX
from users.clinics.serializers import ClinicCardSerializer
from users.clinics.models import ClinicProfile
from ..celery import app

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


@app.task(bind=True)
def update_algolia_record(self, obj, type):
    """
    Update an algolia record

    :param obj: a Clinic or a Case json obj
    :param(str) type: 'clinic' or 'case' to specify obj type
    :return:
    """
    # update algolia record
    client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_SECRET)
    index_name = _get_index(type)
    index = client.init_index(index_name)

    logger.info("Update %s %s from Algolia index '%s'" % (type, obj.get("objectID", ""), index_name))

    index.partial_update_object(obj, {'createIfNotExists': True})
    client.close()


@app.task(bind=True)
def delete_algolia_record(self, uuid, type):
    """
    Delete an algolia record

    :param uuid:
    :param type:
    :return:
    """
    client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_SECRET)
    index_name = _get_index(type)
    index = client.init_index(index_name)
    logger.info("Remove %s %s from Algolia index '%s'" % (type, uuid, index_name))

    index.delete_object(uuid)
    client.close()


@app.task(bind=True)
def update_algolia_clinic_case_num(self, clinic_uuid):
    clinic_obj = get_object_or_None(ClinicProfile, uuid=clinic_uuid)
    if clinic_obj is None:
        # do nothing
        return

    serializer = ClinicCardSerializer(clinic_obj, indexing_algolia=True)
    data = serializer.data

    # TODO: bad. Not sure how to dynamically set fields
    update_algolia_record.delay({"objectID": data["objectID"],
                                 "num_cases": data["num_cases"]}, type="clinic")


def _get_index(type):
    if type == "case":
        return ALGOLIA_CASE_INDEX
    elif type == "clinic":
        return ALGOLIA_CLINIC_INDEX
    else:
        raise ValueError("Parameter type can only be 'case' or 'clinic'.")
