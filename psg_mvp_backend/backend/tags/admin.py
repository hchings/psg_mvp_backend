from django.contrib import admin

from .models import Service


class TagsAdmin(admin.ModelAdmin):
    """
    Customizing Admin Page for Tags Model

    """
    list_display = ('_id', 'category', 'name', 'is_invasive')
    list_filter = ('category', 'is_invasive')
    search_fields = ('name', 'categoory')

    readonly_fields = ('syns', )  # formless field cannot be modified from admin

admin.site.register(Service, TagsAdmin)
