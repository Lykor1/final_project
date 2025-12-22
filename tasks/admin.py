from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'deadline', 'status', 'team', 'created_by', 'assigned_to')
    list_editable = ('status',)
    search_fields = ('title', 'assigned_to', 'created_by')
