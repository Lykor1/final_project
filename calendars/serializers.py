from rest_framework import serializers
from django.utils import timezone

from tasks.models import Task
from meetings.models import Meeting


class CalendarSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    is_past = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    def get_type(self, obj):
        pass

    def get_is_past(self, obj):
        pass

    def get_time(self, obj):
        pass


class CalendarTaskSerializer(CalendarSerializer):
    class Meta:
        model = Task
        fields = ('id', 'type', 'title', 'description', 'deadline', 'status', 'created_by', 'assigned_to', 'team',
                  'is_past', 'time', 'created_at', 'updated_at')
        read_only_fields = fields

    def get_type(self, obj):
        return 'task'

    def get_is_past(self, obj):
        return obj.deadline < timezone.now()

    def get_time(self, obj):
        return obj.deadline


class CalendarMeetingSerializer(CalendarSerializer):
    class Meta:
        model = Meeting
        fields = ('id', 'type', 'topic', 'date', 'start_time', 'end_time', 'creator', 'members', 'full_start_time',
                  'full_end_time', 'is_past', 'time')
        read_only_fields = fields

    def get_type(self, obj):
        return 'meetings'

    def get_is_past(self, obj):
        return obj.full_end_time < timezone.now()

    def get_time(self, obj):
        return obj.full_start_time
