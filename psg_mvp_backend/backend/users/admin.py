"""
Model registration for admin site.

"""
from django.utils.safestring import mark_safe
from django.contrib import admin
from .models import User, RegistrationOTP
from .clinics.models import ClinicProfile
from .doctors.models import DoctorProfile


class UserAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for User Model

    """
    list_display = ('username', 'uuid', 'email', 'user_type',
                    'is_staff')
    list_filter = ('is_staff', 'user_type')
    search_fields = ('username', 'email')
    # raw_id_fields = ('username',)
    ordering = ['user_type', 'uuid']


class ClinicProfileAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for ClinicProfile Model

    """
    list_display = ('display_name', 'user_id', 'uuid', 'logo_img', 'all_doctors_loaded', 'first_check')
    list_filter = ('first_check', 'all_doctors_loaded', 'is_oob')
    search_fields = ['display_name']
    readonly_fields = ['services_raw']

    @mark_safe
    def logo_img(self, obj):
        """
        For diplaying pic in Django admin.
        ref: https://books.agiliq.com/projects/django-admin-cookbook/en/latest/imagefield.html
        :param obj:
        :return:
        """
        if obj.logo:
            return '<img src="%s"  height="50px"/>' % obj.logo.url
        else:
            return 'No_image'

    def changelist_view(self, request, extra_context=None):
        """
        Change list view for non superuser.
        ref: https://stackoverflow.com/questions/19043842/display-different-list-display-depends-on-user
        """
        if not request.user.is_superuser:
            self.list_display = ('display_name', 'logo_img', 'is_oob', 'all_doctors_loaded', 'first_check')
        else:
            self.list_display = ('display_name', 'user_id', 'uuid', 'logo_img', 'all_doctors_loaded', 'first_check')
        return super(ClinicProfileAdmin, self).changelist_view(request, extra_context)


class DoctorProfileAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for ClinicProfile Model

    """
    list_display = ('display_name', 'clinic_name', 'position', 'profile_photo_thumb', 'uuid',
                    'clinic_uuid', 'is_primary', 'relevant', 'first_check')
    list_filter = ('first_check', 'relevant', 'clinic_name')
    search_fields = ['display_name', 'clinic_name']
    readonly_fields = ('uuid', 'clinic_uuid', 'services_raw')

    # ListField in Djongo is formless so could not be edit through Django Admin
    # exclude = ('services_raw',)

    @mark_safe
    def profile_photo_thumb(self, obj):
        """
        For diplaying pic in Django admin.
        ref: https://books.agiliq.com/projects/django-admin-cookbook/en/latest/imagefield.html
        :param obj:
        :return:
        """

        if obj.profile_photo:
            return '<img src="%s" height="70px" />' % obj.profile_photo.url
        else:
            return 'No_image'


class RegistrationOTPAdmin(admin.ModelAdmin):
    list_display = ('hashed_email', 'otp', 'created')
    readonly_fields = ('hashed_email', 'otp', 'created')


admin.site.register(User, UserAdmin)
# admin.site.register(UserProfile)
admin.site.register(ClinicProfile, ClinicProfileAdmin)
admin.site.register(DoctorProfile, DoctorProfileAdmin)
admin.site.register(RegistrationOTP, RegistrationOTPAdmin)
