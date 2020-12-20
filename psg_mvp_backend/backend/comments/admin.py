from django.contrib import admin

from .models import Comment


class CommentAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for Case Model

    """
    list_display = ('uuid', 'case_id', 'author_name', 'posted', 'reply_to_id', 'is_op', 'text')
    list_filter = ('is_op',)
    search_fields = ('uuid', 'text', 'author_name', 'case_id')
    # # raw_id_fields = ('username',)
    # ordering = ['user_type', 'uuid']

    # readonly_fields = ('uuid', 'side_effects')

    # exclude = ('side_effects',)

    def author_name(self, obj):
        return obj.author.name


admin.site.register(Comment, CommentAdmin)
