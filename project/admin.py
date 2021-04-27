from django.contrib import admin
from .models import *

class ProjectAdmin(admin.ModelAdmin):
    model=Project
    # fieldsets = [
    #     (None, {'fields': ['uid','hello','world']}),
    #     ('Date information', {'fields': ['created_at'], 'classes': ['collapse']}),
    # ]

    list_display = (
        'uid',
        'owner',
        'max_contributor',
        'created_at',
        'started_at',
        'finished_at'
    )

    list_filter = ['created_at']

class TaskAdmin(admin.ModelAdmin):
    model=Task

    list_display = (
        'uid',
        'tasker',
        'project',
        'credit',
        'started_at',
        'finished_at'
    )

class ContributionAdmin(admin.ModelAdmin):
    model=Contribution

    list_display = (
        'project',
        'tasker',
        'task_count'
    )


admin.site.register(Project, ProjectAdmin)
admin.site.register(Task,TaskAdmin)
admin.site.register(Contribution,ContributionAdmin)
# admin.site.register(Project)
# Register your models here.
