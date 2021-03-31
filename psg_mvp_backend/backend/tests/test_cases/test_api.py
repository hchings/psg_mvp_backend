from unittest import mock

from django.core.cache import cache
from django.db.models.signals import post_save
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cases.models import Case
from cases.views import CaseList, CaseDetailView
from tests.test_cases.factories import CaseFactory
from tests.test_users.factories import UserFactory, AdminUserFactory


class CaseListCreateTest(APITestCase):
    """
    Test case listing and creation.
    """

    def tearDown(self):
        cache.clear()

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

        case = Case.objects.filter().first()
        self.assertEqual(case.author.name, user.username)
        self.assertEqual(case.author.uuid, str(user.uuid))
        self.assertEqual(case.author.scp_username, '')
        self.assertEqual(case.title, 'MockTitle')
        self.assertEqual(case.recovery_time, '3d')
        self.assertEqual(case.is_official, True)
        self.assertEqual(case.body, '')
        self.assertEqual(case.state, 'reviewing')
        self.assertEqual(case.anesthesia, 'partial')
        self.assertEqual(case.rating, 3)
        self.assertEqual(case.bf_cap, '')
        self.assertListEqual(case.side_effects, ['some text'])
        self.assertListEqual(case.pain_points, ['some text'])
        self.assertEqual(case.clinic.display_name, 'test clinic')
        self.assertEqual(case.clinic.branch_name, 'test branch')
        self.assertEqual(case.clinic.doctor_name, 'test doctor')
        self.assertEqual(case.surgeries[0].name, 'test surgery')
        self.assertEqual(case.surgeries[0].mat, '')
        self.assertEqual(case.surgery_meta.year, 2021)
        self.assertEqual(case.surgery_meta.month, 2)
        self.assertEqual(case.surgery_meta.min_price, 1000)
        self.assertEqual(case.surgery_meta.max_price, 2000)

    def test_create_case(self):
        """
        Test create case.
        """

        url = reverse(CaseList.name)
        user = UserFactory.create()

        data = {
            'author': {
                'name': user.username,
                'uuid': user.uuid,
                'scp_username': ''
            },
            'surgeries': [
                {
                    'name': 'test surgery',
                    'mat': ''
                }
            ],
            'clinic': {
                'display_name': 'test clinic',
                'branch_name': 'test branch',
                'doctor_name': 'test doctor'
            },
            'surgery_meta': {
                'year': '2021',
                'month': '02',
                'min_price': 1000,
                'max_price': 2000
            },
            'body': '',
            'rating': 3,
            'positive_exp': [
                '1',
                '5'
            ],
            'bf_cap': '',
            'title': 'MockTitle',
            'recovery_time': '3d',
            'anesthesia': 'partial',
            'side_effects': [
                'some text'
            ],
            'pain_points': [
                'some text'
            ],
            'is_official': True,
            'state': 'reviewing'
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

    def tearDown(self):
        cache.clear()

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

    def tearDown(self):
        cache.clear()

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


class CaseDetailTest(APITestCase):
    """
    Test case detail API.
    """

    def tearDown(self):
        cache.clear()

    def test_case_detail_get(self):
        """
        Test case detail get API.
        """

        user = UserFactory.create()
        case = CaseFactory.create(username=user.username, uuid=user.uuid, state_choice=Case.STATES[2][0])

        url = reverse(CaseDetailView.name, args=(case.uuid,))

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], case.uuid)
        self.assertEqual(response.data['title'], case.title)
        self.assertEqual(response.data['state'], case.state)

    def _test_case_detail_delete_no_auth(self, url):
        """
        Test case detail delete without authentication.
        """

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_case_detail_delete_with_auth(self, url, user):
        """
        Test case detail delete with authentication.
        """

        self.client.force_authenticate(user)

        self.assertEqual(len(Case.objects.all()), 1)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Case.objects.all()), 0)

    def test_case_detail_delete(self):
        """
        Test case detail delete API.
        """

        user = UserFactory.create()
        case = CaseFactory.create(username=user.username, uuid=user.uuid, state_choice=Case.STATES[2][0])

        url = reverse(CaseDetailView.name, args=(case.uuid,))

        self._test_case_detail_delete_no_auth(url)
        self._test_case_detail_delete_with_auth(url, user)

    def _test_case_detail_patch_no_auth(self, url):
        """
        Test case detail patch without authentication.
        """

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_case_detail_patch_with_auth(self, url, user):
        """
        Test case detail patch with authentication.
        """

        self.client.force_authenticate(user)

        data = {
            'title': 'new title'
        }

        with mock.patch('cases.signals.case_health_check', autospec=True) as mocked_handler:
            post_save.connect(mocked_handler, sender=Case, dispatch_uid='test_cache_mocked_handler')
            response = self.client.patch(url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        case = Case.objects.all().first()
        self.assertEqual(case.title, 'new title')
        self.assertEquals(mocked_handler.call_count, 1)

    def test_case_detail_patch(self):
        """
        Test case detail patch API.
        """

        user = UserFactory.create()
        case = CaseFactory.create(username=user.username, uuid=user.uuid, state_choice=Case.STATES[2][0])

        url = reverse(CaseDetailView.name, args=(case.uuid,))

        self._test_case_detail_patch_no_auth(url)
        self._test_case_detail_patch_with_auth(url, user)

    def _test_case_detail_put_no_auth(self, url):
        """
        Test case detail put without authentication.
        """

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_case_detail_put_with_auth(self, url, user):
        """
        Test case detail put with authentication.
        """

        self.client.force_authenticate(user)

        data = {
            'author': {
                'name': user.username,
                'uuid': user.uuid,
                'scp_username': ''
            },
            'surgeries': [
                {
                    'name': 'test surgery',
                    'mat': ''
                }
            ],
            'clinic': {
                'display_name': 'test clinic',
                'branch_name': 'test branch',
                'doctor_name': 'test doctor'
            },
            'surgery_meta': {
                'year': '2021',
                'month': '02',
                'min_price': 1000,
                'max_price': 2000
            },
            'body': '',
            'rating': 3,
            'positive_exp': [
                '1',
                '5'
            ],
            'bf_cap': '',
            'title': 'MockTitle',
            'recovery_time': '3d',
            'anesthesia': 'partial',
            'side_effects': [
                'some text'
            ],
            'pain_points': [
                'some text'
            ],
            'is_official': True,
            'state': 'reviewing'
        }

        with mock.patch('cases.signals.case_health_check', autospec=True) as mocked_handler:
            post_save.connect(mocked_handler, sender=Case, dispatch_uid='test_cache_mocked_handler')

            response = self.client.put(url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        case = Case.objects.filter().first()
        self.assertEqual(case.author.name, user.username)
        self.assertEqual(case.author.uuid, str(user.uuid))
        self.assertEqual(case.author.scp_username, '')
        self.assertEqual(case.title, 'MockTitle')
        self.assertEqual(case.recovery_time, '3d')
        self.assertEqual(case.is_official, True)
        self.assertEqual(case.body, '')
        self.assertEqual(case.state, 'reviewing')
        self.assertEqual(case.anesthesia, 'partial')
        self.assertEqual(case.rating, 3)
        self.assertEqual(case.bf_cap, '')
        self.assertListEqual(case.side_effects, ['some text'])
        self.assertListEqual(case.pain_points, ['some text'])
        self.assertEqual(case.clinic.display_name, 'test clinic')
        self.assertEqual(case.clinic.branch_name, 'test branch')
        self.assertEqual(case.clinic.doctor_name, 'test doctor')
        self.assertEqual(case.surgeries[0].name, 'test surgery')
        self.assertEqual(case.surgeries[0].mat, '')
        self.assertEqual(case.surgery_meta.year, 2021)
        self.assertEqual(case.surgery_meta.month, 2)
        self.assertEqual(case.surgery_meta.min_price, 1000)
        self.assertEqual(case.surgery_meta.max_price, 2000)

        # Check if the signal is called once.
        self.assertEquals(mocked_handler.call_count, 1)

    def test_case_detail_put(self, ):
        """
        Test case detail put API.
        """

        user = UserFactory.create()
        case = CaseFactory.create(username=user.username, uuid=user.uuid, state_choice=Case.STATES[2][0])

        url = reverse(CaseDetailView.name, args=(case.uuid,))

        self._test_case_detail_put_no_auth(url)
        self._test_case_detail_put_with_auth(url, user)

# class CaseSearchTest(APITestCase):
#     """
#     Test case search.
#     """
#
#     def tearDown(self):
#         cache.clear()
#
#     def _test_empty_search_query(self, url):
#         """
#         Test empty search query.
#         """
#
#         response = self.client.post(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#     def test_case_search(self):
#         """
#         Test case search.
#         """
#
#         url = reverse(CaseSearchView.name)
#         user = UserFactory.create()
#         case = CaseFactory.create(username=user.username, uuid=user.uuid, state_choice=Case.STATES[2][0])
#
#         CaseIndexCommand.load_index(wipe_out=True)
#
#         self._test_empty_search_query(url)
#
#         data = {
#             'title': case.title,
#             'is_official': case.is_official
#         }
#
#         response = self.client.post(url, data)
#
#         print(response.status_code)
#         print(response.data)
#         print(case.state)
