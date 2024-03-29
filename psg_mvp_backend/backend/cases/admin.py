"""
Model registration for admin site for Case.

"""
from annoying.functions import get_object_or_None
from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Case, CaseImages, CaseInviteToken, Hit, PricePoint

user_model = get_user_model()

class CaseAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for Case Model

    """
    list_display = ('uuid', 'created', 'posted', 'status', 'is_scrapped', 'consent', 'skip', 'skip_reason', 'title', 'is_official',
                    'author', 'author_uuid',)
    list_filter = ('state', 'consent', 'skip', 'skip_reason', 'is_official', 'gender', 'interest', 'failed')
    search_fields = ('uuid', 'author', 'title')
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


class CaseInviteTokenAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for CaseInviteToken Model
    """
    list_display = ('username', 'user_code', 'user_uuid', 'token', 'created_at')

    def username(self, obj):
        try:
            user_obj = user_model.objects.get(uuid=obj.user_uuid)
            return user_obj.username
        except:
            return ''

class HitAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for Hit Model
    """
    list_display = ('created', 'user', 'ip', 'session', 'user_agent', 'hitcount')


class PricePointAdmin(admin.ModelAdmin):
    list_display = ('_id', 'clinic_uuid', 'surgeries', 'min_price', 'max_price')

    def surgeries(self, obj):
        return ", ".join([item.name for item in obj.surgeries])

    def min_price(self, obj):
        return obj.surgery_meta.min_price

    def max_price(self, obj):
        return obj.surgery_meta.max_price


admin.site.register(Case, CaseAdmin)
admin.site.register(CaseImages, CaseImagesAdmin)
admin.site.register(CaseInviteToken, CaseInviteTokenAdmin)
admin.site.register(Hit, HitAdmin)
admin.site.register(PricePoint, PricePointAdmin)
