"""
Test Clinic relevant APIs.
"""
from random import randint

from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from tests.test_users.factories import UserFactory
from users.clinics.views import ClinicPublicDetail
from users.clinics.models import ClinicProfile


class ClinicAPITest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ClinicPublicDetail.as_view()
        self.uri = '/clinics/'
        self.user = self.setup_clinic_user()
        self.token = Token.objects.create(user=self.user)
        self.token.save()
        self.data = {
            "display_name": "晶華美醫診所",
            "services_raw": ["test2"],
            "instagram_url": "http://my-insta-2.com",
            "branches": [
                {
                    "branch_name": "總店erin",
                    "place_id": "ChIJ004m5WipQjQRmBN9dV20Vj412345",
                    "is_head_quarter": True,
                    "address": "台北市中山區中山北路二段39巷2-2號3F",
                    "address_help_text": "捷運淡水信義線中山站3號出口",
                    "region": "台北市",
                    "locality": "中山區",
                    "phone": "+886225111000",
                    "er": 123
                }
            ]
        }

    @staticmethod
    def setup_clinic_user():
        User = get_user_model()
        user = User.objects.create_user(
            'test',
            email='testuser@test.com',
            password='test',
            user_type='clinic'
        )
        user.save()
        objs = ClinicProfile.objects.all()
        clinic_profile_obj = ClinicProfile.objects.get(user_id=str(getattr(user, '_id', '')))
        # TODO: code should make this association automatically
        user.clinic_uuid = clinic_profile_obj.uuid
        user.save()
        return user

    def test_list_a_clinic(self):
        """
        Test GET /clinics/<uuid>
        :return:
        """
        response = self._call_clinic_detail_api("GET")
        # print("get response", response.data)
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))

    def test_update_clinic(self):
        """
        Test PUT /clinics/<uuid> on non-nested fields
        :return:
        """
        self.data["instagram_url"] = "http://my-insta-3.com"
        response = self._call_clinic_detail_api("PUT")
        clinic_obj = ClinicProfile.objects.get(uuid=self.user.clinic_uuid)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(clinic_obj.instagram_url, self.data["instagram_url"])

    def test_update_clinic_branch(self):
        """
        Test PUT /clinics/<uuid> on nested field
        :return:
        """
        self.data["branches"][0]["branch_name"] = "new-branch-name"
        response = self._call_clinic_detail_api("PUT")
        clinic_obj = ClinicProfile.objects.get(uuid=self.user.clinic_uuid)

        # print("get response", response.data, response.data["branches"][0]["branch_name"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(clinic_obj.branches[0].branch_name, self.data["branches"][0]["branch_name"])

    def test_have_existing_branch_and_add_new_branch(self):
        """
        Test PUT /clinics/<uuid>
        Create a new branch when there's an existing branch
        :return:
        """

        response = self._call_clinic_detail_api("PUT")
        self.assertEqual(response.status_code, 200)

        place_uuid_new = str(randint(0, 10000))
        self.data["branches"][0]["place_id"] = place_uuid_new
        self.data["branches"][0]["branch_name"] = "a new branch"
        self.assertEqual(response.status_code, 200)
        response = self._call_clinic_detail_api("PUT")

        clinic_obj = ClinicProfile.objects.get(uuid=self.user.clinic_uuid)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(clinic_obj.branches) == 2)
        self.assertEqual(clinic_obj.branches[-1].place_id, place_uuid_new)

    def test_add_two_new_clinic_branch(self):
        """
        Test PUT /clinics/<uuid> on nested field
        :return:
        """
        # add a new branch
        place_uuid_new = str(randint(0, 10000))
        self.data["branches"].append(self.data["branches"][0].copy())
        self.data["branches"][1]["place_id"] = place_uuid_new
        self.data["branches"][1]["branch_name"] = "a new branch"
        response = self._call_clinic_detail_api("PUT")
        clinic_obj = ClinicProfile.objects.get(uuid=self.user.clinic_uuid)
        # print(clinic_obj.branches)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(clinic_obj.branches) == 2)
        self.assertEqual(clinic_obj.branches[-1].place_id, place_uuid_new)

    def test_anonymous_put_permission_denial(self):
        """
        Test PUT /clinics/<uuid> w/ non authenticated user
        :return:
        """
        response = self._call_clinic_detail_api("PUT", token_key="123")

        self.assertEqual(response.status_code, 401,
                         'Expected Response Code 401, received {0} instead.'
                         .format(response.status_code))

    def test_non_owner_put_permission_denial(self):
        """
        Test PUT /clinics/<uuid> w/ authenticated but not clinic owner user
        :return:
        """
        # create a random, non-clinic user
        random_user = UserFactory.create()
        token = Token.objects.create(user=random_user)
        token.save()

        response = self._call_clinic_detail_api("PUT", token_key=token.key)
        self.assertEqual(response.status_code, 403,
                         'Expected Response Code 401, received {0} instead.'
                         .format(response.status_code))

    def _call_clinic_detail_api(self, verb, data=None, token_key=None):
        """
        Helper function to call Clinic detail (/clinics/<uuid>) API
        :param verb:
        :param data:
        :param token_key:
        :return:
        """
        uri = self.uri + str(self.user.clinic_uuid)
        if not data:
            data = self.data
        if not token_key:
            token_key = self.token.key

        if verb == "PUT":
            request = self.factory.put(uri, data, HTTP_AUTHORIZATION='Token {}'.format(token_key))
        elif verb == "GET":
            request = self.factory.get(uri)

        response = self.view(request, uuid=str(self.user.clinic_uuid))
        return response
