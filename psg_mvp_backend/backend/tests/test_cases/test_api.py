from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cases.views import CaseList
from tests.test_cases.factories import CaseFactory
from tests.test_users.factories import UserFactory, AdminUserFactory


class CaseListCreateTest(APITestCase):
    """
    Test case listing and creation.
    """

    def _test_create_case_no_auth(self, url, data):
        """
        Test create case without authenticating the user.
        """

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_create_case_with_auth(self, url, data, user):
        """
        Test create case after authenticating the user.
        """

        self.client.force_authenticate(user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

    def test_create_case(self):
        """
        Test create case.
        """

        url = reverse(CaseList.name)
        user = UserFactory.create()

        data = {
            "author": {
                "name": user.username,
                "uuid": user.uuid,
                "scp_username": ""
            },
            "surgeries": [
                {
                    "name": "墊下巴",
                    "mat": ""
                }
            ],
            "clinic": {
                "display_name": "悠美診所",
                "branch_name": "忠孝店",
                "doctor_name": "劉厚耕"
            },
            "surgery_meta": {
                "year": "2021",
                "month": "02",
                "min_price": 1000,
                "max_price": 2000
            },
            "body": "",
            "rating": 3,
            "positive_exp": [
                "1",
                "5"
            ],
            "bf_cap": "",
            "title": "MockTitle",
            "recovery_time": "3d",
            "anesthesia": "partial",
            "side_effects": [
                "some text"
            ],
            "pain_points": [
                "somt text"
            ],
            "is_official": True,
            "state": "reviewing"
        }

        self._test_create_case_no_auth(url, data)
        self._test_create_case_with_auth(url, data, user)

    def _test_list_case_no_auth(self, url):
        """
        Test list case without authenticating the user.
        """

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_list_case_normal_user_with_auth(self, url, user):
        """
        Test list case after authenticating the normal user.
        """

        self.client.force_authenticate(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_list_case_admin_user_with_auth(self, url, admin_user):
        """
        Test list case after authenticating the admin user.
        """

        self.client.force_authenticate(admin_user)

        # No case object exits
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

        # Case objects exists
        CaseFactory.create(username=admin_user.username, uuid=admin_user.uuid)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_case(self):
        """
        Test list case.
        """

        url = reverse(CaseList.name)
        user = UserFactory.create()
        admin_user = AdminUserFactory.create()

        self._test_list_case_no_auth(url)
        self._test_list_case_normal_user_with_auth(url, user)
        self._test_list_case_admin_user_with_auth(url, admin_user)


class CaseLikeTest(APITestCase):
    """
    Test case like.
    """

    def _test_case_like_no_auth(self, url):
        """
        Test like case without authenticating the user.
        """

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_case_like_no_valid_case(self, url, user):
        """
        Test case like when no valid case exists.
        """

        self.client.force_authenticate(user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _test_case_like_valid_case(self, url, user):
        """
        Test case like when no valid case exists.
        """

        self.client.force_authenticate(user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_case_like(self):
        """
        Test case like.
        """

        url = reverse('like-case', args=(123,))
        self._test_case_like_no_auth(url)

        user = UserFactory.create()
        self._test_case_like_no_valid_case(url, user)

        case = CaseFactory.create(username=user.username, uuid=user.uuid)
        url = reverse('like-case', args=(case.uuid,))
        self._test_case_like_valid_case(url, user)


class CaseUnLikeTest(APITestCase):
    """
    Test case unlike.
    """

    def _test_case_unlike_no_auth(self, url):
        """
        Test unlike case without authenticating the user.
        """

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_case_unlike_no_valid_case(self, url, user):
        """
        Test case unlike when no valid case exists.
        """

        self.client.force_authenticate(user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _test_case_unlike_valid_case(self, url, user):
        """
        Test case unlike when no valid case exists.
        """

        self.client.force_authenticate(user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_case_unlike(self):
        """
        Test case unlike.
        """

        url = reverse('unlike-case', args=(123,))
        self._test_case_unlike_no_auth(url)

        user = UserFactory.create()
        self._test_case_unlike_no_valid_case(url, user)

        case = CaseFactory.create(username=user.username, uuid=user.uuid)
        url = reverse('unlike-case', args=(case.uuid,))
        self._test_case_unlike_valid_case(url, user)
