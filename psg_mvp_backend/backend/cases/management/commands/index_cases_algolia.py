"""
Index cases into Algolia
    >> python manage.py index_cases_algolia
"""
from random import randint

from django.core.management.base import BaseCommand

from algoliasearch.search_client import SearchClient

from cases.serializers import CaseCardSerializer
from cases.models import Case



class Command(BaseCommand):
    """
    Delete the exisiting cases index in ES instance
    and bulk insert all "published" cases from main DB.
    """

    help = 'Indexes Cases in Elastic Search'

    def handle(self, *args, **options):
        client = SearchClient.create('59Z1FVS3D5', '7a3a8ca34511873b56938d40f34b125d')
        index = client.init_index('cases')
        cases = Case.objects.filter(state="published")
        # cases = cases[:10]
        serializer = CaseCardSerializer(cases, many=True, search_view=True)
        # print(serializer.data)

        # algolia require object id
        for obj in serializer.data:
            obj["objectID"] = obj["uuid"]
            obj["age"] = randint(18, 70)
            # tmp
            ROOT_URL = "http://localhost:8000"
            if obj["af_img_thumb"]:
                obj["af_img_thumb"] = ROOT_URL + obj["af_img_thumb"]

            if obj["bf_img_thumb"]:
                obj["bf_img_thumb"] = ROOT_URL + obj["bf_img_thumb"]
            pivot = randint(0, 10)
            if pivot // 2 == 0:
                obj["gender"] = "female"
            else:
                obj["gender"] = "male"


        print("indexing...")
        index.replace_all_objects(serializer.data)
        print("done")
