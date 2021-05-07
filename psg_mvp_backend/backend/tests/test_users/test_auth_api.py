from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cases.models import Case
from comments.models import Comment
from tests.test_cases.factories import CaseFactory
from tests.test_comments.factories import CommentFactory
from tests.test_users.factories import UserFactory
from users.models import RegistrationOTP, User
from users.serializers import USER_TYPES
from users.views import RegisterViewEx, LoginViewEx, UserInfoView


class UserLoginTest(APITestCase):
    """
    Tests user login.
    """

    def _test_valid_user(self, url, data):
        """
        Test valid user login.
        """

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _test_invalid_user(self, url, data):
        """
        Test invalid user login.
        """

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """
        Test user login.
        """

        url = reverse(LoginViewEx.name)
        user = UserFactory.create()
        data = {
            'username': user.username,
            'email': user.email,
            'password': 'testpassword'
        }

        self._test_valid_user(url, data)

        data['password'] = 'wrongpassword'
        self._test_invalid_user(url, data)


class UserRegistrationTest(APITestCase):
    """
    Tests user registration.
    """

    def _test_generate_otp(self, url, data):
        """
        Test OTP generation.
        """

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Generate OTP

        otp_objects = RegistrationOTP.objects.all()
        users = User.objects.all()
        self.assertEqual(len(otp_objects), 1)
        self.assertEqual(len(users), 0)

    def _test_random_otp(self, url, data):
        """
        Test random OTP.
        """

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Validate with random OTP

        users = User.objects.all()
        self.assertEqual(len(users), 0)

    def _test_correct_otp(self, url, data):
        """
        Test corrct OTP.
        """

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Validate with correct OTP

        users = User.objects.all()
        self.assertEqual(len(users), 1)

    def test_user_registration(self):
        """
        Test user registration.
        """

        url = reverse(RegisterViewEx.name)
        data = {
            'username': 'testuser',
            'email': 'testuser@testuser.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'user_type': USER_TYPES[0],
            'otp': ''
        }

        self._test_generate_otp(url, data)

        data['otp'] = 'RANDOM'
        self._test_random_otp(url, data)

        otp_objects = RegistrationOTP.objects.all()
        data['otp'] = otp_objects[0].otp
        self._test_correct_otp(url, data)


class UserInfoTest(APITestCase):
    """
    Tests user info get and patch.
    """

    def test_get_user_info(self):
        """
        Test get user info.
        """

        url = reverse(UserInfoView.name)
        user = UserFactory.create()

        # Create a draft case
        CaseFactory.create(username=user.username, uuid=user.uuid, state_choice=Case.STATES[0][0])
        self.client.force_authenticate(user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['draft'], 1)

    def test_patch_user_info(self):
        """
        Test patch user info.
        """

        url = reverse(UserInfoView.name)
        user = UserFactory.create()

        # Create a draft case
        CaseFactory.create(username=user.username, uuid=user.uuid, state_choice=Case.STATES[0][0])

        # Create a comment
        CommentFactory.create(username=user.username, uuid=user.uuid)

        self.client.force_authenticate(user)

        new_username = 'newusername'
        new_gender = User.GENDERS[0][0]

        data = {
            'userName': new_username,
            'gender': new_gender
        }

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(user.username, new_username)
        self.assertEqual(user.gender, new_gender)

        cases = Case.objects.filter(author={'uuid': str(user.uuid)})
        self.assertEqual(len(cases), 1)
        for case in cases:
            self.assertEqual(case.author.name, new_username)

        comments = Comment.objects.filter(author={'uuid': str(user.uuid)})
        self.assertEqual(len(comments), 1)
        for comment in comments:
            self.assertEqual(comment.author.name, new_username)
