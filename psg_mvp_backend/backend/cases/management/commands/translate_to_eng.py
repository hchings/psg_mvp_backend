"""
Translate cases subjects to English (for US demo)

    >> python manage.py translate_to_eng

"""

import json
import re, os

from django.core.management.base import BaseCommand

from algoliasearch.search_client import SearchClient
from googletrans import Translator
from hanziconv import HanziConv

from cases.models import Case, SurgeryTag
from cases.serializers import CaseCardSerializer
from backend.settings import FIXTURE_ROOT


TRANSLATE_FILE = os.path.join(FIXTURE_ROOT, 'procedure_zh_to_en.json')


class Command(BaseCommand):
    """
    Delete the exisiting cases index in ES instance
    and bulk insert all "published" cases from main DB.
    """

    help = 'Englishfy cases'

    def handle(self, *args, **options):
        client = SearchClient.create('59Z1FVS3D5', '7a3a8ca34511873b56938d40f34b125d')
        index = client.init_index('cases')

        translator = Translator()

        # readin json
        with open(TRANSLATE_FILE) as json_file:
            procedure_map = json.load(json_file)

        new_cases = []
        cases = Case.objects.filter(state="published")
        for i, case in enumerate(cases):
            try:
                title_simplified = HanziConv.toSimplified(case.title)
                if title_simplified[1:].startswith('缝双眼皮超快恢复 3 週心得'):
                    title_simplified = title_simplified[1:]

                title_en = translator.translate(title_simplified, dest='en').text
                # further remove chinese
                regex = re.compile('[^\u0020-\u024F]')
                title_en = regex.sub('', title_en)

                print("%s -> %s" % (title_simplified, title_en))
                case.title = title_en

                # surgeries
                surgeries_objs = []
                dedup = set()
                for surgery in case.surgeries:
                    surgery_tag = SurgeryTag(name=procedure_map.get(surgery.name, surgery.name),
                                             mat=procedure_map.get(surgery.mat, surgery.mat))
                    if surgery_tag.name not in dedup:
                        surgeries_objs.append(surgery_tag)
                        dedup.add(surgery_tag.name)
                    case.surgeries = surgeries_objs
                    print(surgeries_objs)

                # modify DB data
                case.save()
                new_cases.append(case)

            except Exception as e:
                print("ERROR:", e)

        # update algolia
        serializer = CaseCardSerializer(new_cases,
                                        many=True,
                                        search_view=True)

        print("=======update algolia========")
        objs_final = []
        for obj in serializer.data:
            obj_new = {}
            obj_new["objectID"] = obj["uuid"]
            obj_new["surgeries"] = obj["surgeries"]
            obj_new["title"] = obj["title"]
            if obj["gender"]:
                obj_new["gender"] = obj["gender"].capitalize()
            objs_final.append(obj_new)

        print(objs_final)
        # open this to update data in Algolia
        # index.partial_update_objects(objs_final)
