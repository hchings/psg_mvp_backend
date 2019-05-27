"""
Model registration for admin site.

"""

from django.contrib import admin
from .models import User
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
    list_display = ('display_name', 'user_id', 'uuid', 'all_doctors_loaded', 'first_check')
    list_filter = ('first_check', 'all_doctors_loaded', 'is_oob')
    search_fields = ['display_name']


class DoctorProfileAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for ClinicProfile Model

    """
    list_display = ('display_name', 'clinic_name', 'position', 'uuid', 'clinic_uuid', 'is_primary', 'relevant', 'first_check')
    list_filter = ('first_check', 'relevant', 'clinic_name')
    search_fields = ['display_name', 'clinic_name']
    readonly_fields = ('uuid', 'clinic_uuid')
    # ListField in Djongo is formless so could not be edit through Django Admin
    exclude = ('professions_raw',)


admin.site.register(User, UserAdmin)
# admin.site.register(UserProfile)
admin.site.register(ClinicProfile, ClinicProfileAdmin)
admin.site.register(DoctorProfile, DoctorProfileAdmin)
