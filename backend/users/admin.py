"""
Model registration for admin site.

"""

from django.contrib import admin
from .models import User
from .clinics.models import ClinicProfile


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

    # list_display = ('username', 'uuid', 'email', 'user_type',
    #                 'is_staff', 'user_profile')
    # list_filter = ('is_staff', 'user_type')
    # search_fields = ('username', 'email')
    # # raw_id_fields = ('username',)
    # ordering = ['user_type', 'uuid']


class ClinicProfileAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for ClinicProfile Model

    """
    list_display = ('display_name', 'user_id', 'uuid')

#
# class ClinicBranchAdmin(admin.ModelAdmin):
#     """
#     Customizing Admin Page for ClinicBranch Model
#
#     """
#     list_display = ('display_name', 'id', 'is_head_quarter',
#                     'place_id', 'rating', 'region', 'locality',
#                     'phone', 'opening_info')
#     list_filter = ('region', )
#     # raw_id_fields = ('username',)
#     # ordering = ['user_type', 'uuid']
#
#     def display_name(self, obj):
#         """Get string representation"""
#         return str(obj)


admin.site.register(User, UserAdmin)
# admin.site.register(UserProfile)
# admin.site.register(DoctorProfile)
admin.site.register(ClinicProfile, ClinicProfileAdmin)
# admin.site.register(ClinicBranch, ClinicBranchAdmin)
