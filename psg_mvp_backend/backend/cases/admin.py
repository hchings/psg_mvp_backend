"""
Model registration for admin site for Case.

"""
from annoying.functions import get_object_or_None
from django.contrib import admin

from .models import Case, CaseImages


class CaseAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for Case Model

    """
    list_display = ('uuid', 'created', 'posted', 'status', 'is_scrapped', 'title', 'is_official', 'gender', 'rating',
                    'author', 'author_uuid', 'clinic_branch', 'clinic_uuid', 'doctor', 'doctor_profile_id')
    # list_filter = ('is_staff', 'user_type')
    # search_fields = ('username', 'email')
    # raw_id_fields = ('username',)
    # ordering = ['user_type', 'uuid']

    readonly_fields = ('uuid', 'side_effects', 'pain_points')

    # exclude = ('clinic_exp',)

    def author(self, obj):
        try:
            return obj.author.name
        except Exception:
            return ''

    def author_uuid(self, obj):
        try:
            return obj.author.uuid
        except Exception:
            return ''

    def clinic_branch(self, obj):
        try:
            return ' / '.join([obj.clinic.display_name, obj.clinic.branch_name])
        except Exception:
            return ''

    def clinic_uuid(self, obj):
        try:
            return obj.clinic.uuid
        except Exception:
            return ''

    def doctor(self, obj):
        try:
            return obj.clinic.doctor_name
        except Exception:
            return ''

    def doctor_profile_id(self, obj):
        try:
            return obj.clinic.doctor_profile_id
        except Exception:
            return ''

    def status(self, obj):
        # TODO: double check this
        try:
            if int(obj.state) > 0:
                return Case.STATES[int(obj.state)][0]
        except ValueError as e:
            # is string
            return obj.state

    def is_scrapped(self, obj):
        return obj.author.scp or False


class CaseImagesAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for CaseImages Model
    """
    list_display = ('_id', 'order', 'case_title', 'case_uuid', 'caption')

    def case_title(self, obj):
        """
        Display case title in admin page for convenience.
        :param obj:
        :return:
        """
        case_obj = get_object_or_None(Case, uuid=obj.case_uuid)
        return '' if not case_obj else case_obj.title


admin.site.register(Case, CaseAdmin)
admin.site.register(CaseImages, CaseImagesAdmin)
