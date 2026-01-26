from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model

from tasks.models import Task
from meetings.models import Meeting

User = get_user_model()


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
    created_by = serializers.SerializerMethodField()
    assigned_to = serializers.SerializerMethodField()
    team = serializers.CharField(source='team.name', read_only=True)

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

    def get_created_by(self, obj):
        return f'{obj.created_by.email} ({obj.created_by.first_name} {obj.created_by.last_name})'

    def get_assigned_to(self, obj):
        if obj.assigned_to:
            return f'{obj.assigned_to.email} ({obj.assigned_to.first_name} {obj.assigned_to.last_name})'
        return None


class MembersSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'full_name')
        read_only_fields = fields

    def get_full_name(self, obj):
        return f'{obj.first_name.strip()} {obj.last_name.strip()}'


class CalendarMeetingSerializer(CalendarSerializer):
    creator = serializers.SerializerMethodField()
    members = MembersSerializer(read_only=True, many=True)

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

    def get_creator(self, obj):
        return f'{obj.creator.email} ({obj.creator.first_name} {obj.creator.last_name})'
