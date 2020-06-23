from django.contrib import admin

from .models import Review


class ReviewAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for Review Model

    """
    list_display = ('uuid', 'hash', 'posted', 'scp_time', 'scp',
                    'author_name', 'rating', 'body',
                    'clinic', 'doctors', 'source')
    list_filter = ('rating', 'source')
    search_fields = ('body', 'clinic')
    # # raw_id_fields = ('username',)
    # ordering = ['user_type', 'uuid']

    # readonly_fields = ('uuid', 'side_effects')

    # exclude = ('side_effects',)

    def scp(self, obj):
        return obj.author.scp

    def author_name(self, obj):
        return obj.author.name or obj.author.scp_username

    def clinic(self, obj):
        return '%s | %s' % (obj.clinic.display_name, obj.clinic.branch_name) if obj.clinic.display_name else ''

    def doctors(self, obj):
        return str(obj.doctors)
        # return '%s | %s' % (obj.clinic.doctor_name, obj.clinic.doctor_profile_id) if obj.clinic.doctor_name else ''


admin.site.register(Review, ReviewAdmin)
