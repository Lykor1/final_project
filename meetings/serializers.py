from django.contrib.auth import get_user_model
from rest_framework import serializers

from meetings.models import Meeting

User = get_user_model()


class MeetingCreateSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True,
        slug_field='email',
        queryset=User.objects.all()
    )

    class Meta:
        model = Meeting
        fields = ('topic', 'date', 'start_time', 'end_time', 'members')


class MeetingMembersSerializer(serializers.ModelSerializer):
    team_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'full_name', 'age', 'role', 'team_name')
        read_only_fields = fields

    def get_team_name(self, obj):
        if not obj.team:
            return None
        return obj.team.name

    def get_age(self, obj):
        if not obj.birthday:
            return None
        return obj.get_age

    def get_full_name(self, obj):
        return f'{obj.first_name.strip()} {obj.last_name.strip()}'


class MeetingListSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    members = MeetingMembersSerializer(many=True, read_only=True, source='members.all')

    class Meta:
        model = Meeting
        fields = ('id', 'topic', 'date', 'start_time', 'end_time', 'creator', 'members')

    def get_creator(self, obj):
        return f'{obj.creator.first_name.strip()} {obj.creator.last_name.strip()}'
