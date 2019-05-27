"""
Unittests for models in Users app.

"""
from bson import ObjectId

from annoying.functions import get_object_or_None

from django.test import TestCase

from users.models import User
from users.clinics.models import ClinicProfile
from users.doctors.models import DoctorProfile


class UserTest(TestCase):
    """
    Test cases for serUSERPROFILE model.

    """
    def setUp(self):
        pass

    @staticmethod
    def create_user(user_type='user', email='dummy@gmail.com', username='dummy'):
        return User.objects.create(email=email,
                                   username=username,
                                   user_type=user_type)

    def test_create_clinic_user(self):
        clinic_obj = self.create_user(user_type='clinic')
        # ensure uuid
        self.assertIsNotNone(clinic_obj.uuid)
        # ensure a corresponding profile object is created
        document_id = str(getattr(clinic_obj, '_id', ''))
        clinic_profile_obj = get_object_or_None(ClinicProfile, user_id=ObjectId(document_id))
        self.assertIsNotNone(clinic_profile_obj)
        self.assertEqual(clinic_profile_obj.user_id, document_id)
        self.assertEqual(str(clinic_profile_obj.uuid), str(clinic_obj.uuid))
        self.assertEqual(str(clinic_profile_obj.display_name), str(clinic_obj.username))

    def test_create_doctor_user(self):
        doctor_obj = self.create_user(user_type='doctor')
        # ensure uuid
        self.assertIsNotNone(doctor_obj.uuid)
        # ensure a corresponding profile object is created
        document_id = str(getattr(doctor_obj, '_id', ''))
        doctor_profile_obj = get_object_or_None(DoctorProfile, uuid=doctor_obj.uuid)
        self.assertIsNotNone(doctor_profile_obj)
        # ensure links with doctor user
        self.assertEqual(doctor_profile_obj.user_id, document_id)
        self.assertEqual(str(doctor_profile_obj.uuid), str(doctor_obj.uuid))
        self.assertEqual(str(doctor_profile_obj.display_name), str(doctor_obj.username))
        # ensure Equal(str(doctor_profile_obj), )

    def test_link_doctor_with_clinic(self):
        doctor_obj = self.create_user(user_type='doctor')
        clinic_obj = self.create_user(user_type='clinic',
                                      email='clinic@gmail.com',
                                      username='clinic')

        doctor_profile_obj = get_object_or_None(DoctorProfile, uuid=doctor_obj.uuid)

        # test add non-exist clinic
        doctor_profile_obj.clinic_name = 'nonexist_clinic'
        doctor_profile_obj.save()
        self.assertEqual(doctor_profile_obj.clinic_uuid, '')

        # test add exist clinic
        doctor_profile_obj.clinic_name = 'clinic'
        doctor_profile_obj.save()
        self.assertEqual(doctor_profile_obj.clinic_uuid, str(clinic_obj.uuid))

        # test display str
        self.assertEqual(str(doctor_profile_obj), 'clinic_dummy')







