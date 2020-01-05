from django.contrib import admin

from .models import Case


class CaseAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for Case Model

    """
    # list_display = ('username', 'uuid', 'email', 'user_type',
    #                 'is_staff')
    # list_filter = ('is_staff', 'user_type')
    # search_fields = ('username', 'email')
    # # raw_id_fields = ('username',)
    # ordering = ['user_type', 'uuid']

    readonly_fields = ('uuid', 'side_effects')

    exclude = ('side_effects',)


admin.site.register(Case, CaseAdmin)
