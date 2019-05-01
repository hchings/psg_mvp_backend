"""
Unittests for Users API in Users app.
"""

# from rest_framework.test import APIRequestFactory


from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from django.urls import reverse

# from backend.shared.testing_utils import get_new_user
from users.clinics.views import ClinicPublicList
from users.clinics.models import ClinicProfile


class UsersAPITest(APITestCase):
    """
    Test cases for Users API.

    """
    CLINIC_ROOT_URL = reverse(ClinicPublicList.name)
    client = None

    def setUp(self):
        """
        Force login a user.

        """
        print(self.CLINIC_ROOT_URL)
        self.client = APIClient()
        # TODO: create clinic profile here
        # self.client.force_authenticate(user=self.user)

    def _assert_request(self, url, http_verb, expected, payload=None):
        """
        Send a request and validate response state.

        """
        response = getattr(self.client, http_verb)(url, payload)
        self.assertEqual(response.status_code, expected)

    # TODO: WIP
    def test_get_a_clinic(self):
        # self.assertEqual(True, True)
        pass

    # TODO: WIP
    def test_get_clinics(self):
        """
        Ensure anyone can browse.

        """
        self._assert_request(self.CLINIC_ROOT_URL,
                             'get',
                             status.HTTP_200_OK)
