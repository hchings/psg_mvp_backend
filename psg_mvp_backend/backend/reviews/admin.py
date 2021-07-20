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

    readonly_fields = ('services',)

    def scp(self, obj):
        return obj.author.scp

    def author_name(self, obj):
        return obj.author.name or obj.author.scp_username

    def clinic(self, obj):
        return '%s | %s' % (obj.clinic.display_name, obj.clinic.branch_name) if obj.clinic.display_name else ''

    def doctors(self, obj):
        return str(obj.doctors)


admin.site.register(Review, ReviewAdmin)
