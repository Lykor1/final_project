from django.contrib import admin

from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('topic', 'date', 'start_time', 'end_time', 'creator', 'reminder_1hour_sent')
