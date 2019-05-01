"""
Unittests for models in Users app.

"""
from bson import ObjectId

from annoying.functions import get_object_or_None

from django.test import TestCase

from users.models import User
from users.clinics.models import ClinicProfile


class UserTest(TestCase):
    """
    Test cases for serUSERPROFILE model.

    """
    def setUp(self):
        pass

    @staticmethod
    def create_user(user_type='user'):
        return User.objects.create(email='dummy@gmail.com',
                                   username='dummy',
                                   user_type=user_type)

    def test_create_clinic_user(self):
        clinic_obj = self.create_user(user_type='clinic')
        # ensure uuid
        self.assertIsNotNone(clinic_obj.uuid)
        # ensure a corresponding
        document_id = str(getattr(clinic_obj, '_id', ''))
        clinic_profile_obj = get_object_or_None(ClinicProfile, user_id=ObjectId(document_id))
        self.assertIsNotNone(clinic_profile_obj)
        self.assertEqual(clinic_profile_obj.user_id, document_id)
        self.assertEqual(str(clinic_profile_obj.uuid), str(clinic_obj.uuid))
        self.assertEqual(str(clinic_profile_obj.display_name), str(clinic_obj.username))