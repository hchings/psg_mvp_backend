"""
Model registration for admin site for Case.

"""

from django.contrib import admin

from .models import Case


class CaseAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for Case Model

    """
    list_display = ('uuid', 'posted', 'status', 'title', 'is_official', 'gender','rating',
                    'author', 'author_uuid', 'clinic_branch', 'clinic_uuid', 'doctor')
    # list_filter = ('is_staff', 'user_type')
    # search_fields = ('username', 'email')
    # raw_id_fields = ('username',)
    # ordering = ['user_type', 'uuid']

    readonly_fields = ('uuid', 'side_effects')

    # exclude = ('side_effects',)

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

    def status(self, obj):
        # TODO: double check this
        try:
            if int(obj.state) > 0:
                return Case.STATES[int(obj.state)][0]
        except ValueError as e:
            # is string
            return obj.state


admin.site.register(Case, CaseAdmin)
