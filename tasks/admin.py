from django.contrib import admin

from .models import Task, Comment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'deadline', 'status', 'team', 'created_by', 'assigned_to')
    list_editable = ('status',)
    search_fields = ('title', 'assigned_to', 'created_by')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'text', 'created_at')
    search_fields = ('author', 'task')
