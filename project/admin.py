from django.contrib import admin
from .models import Project

class ProjectAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['uid','hello','world']}),
        ('Date information', {'fields': ['created_at'], 'classes': ['collapse']}),
    ]

    # list_display=('list1', 'list2')

    list_filter = ['created_at']

admin.site.register(Project, ProjectAdmin)
# admin.site.register(Project)
# Register your models here.
