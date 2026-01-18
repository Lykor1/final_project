from datetime import timedelta

import pytest
from django.utils import timezone
from freezegun import freeze_time

from calendars.serializers import CalendarMeetingSerializer, CalendarTaskSerializer


@pytest.mark.serializers
@pytest.mark.django_db
class TestCalendarTaskSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, create_team, team_data, create_user, user_data, task_data,
              create_task):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.user = create_user(team=self.team, **user_data)
        self.task = create_task(created_by=self.admin, team=self.team, assigned_to=self.user, **task_data)

    def test_task_serializer_fields(self):
        """
        Тест на отображение полей сериализатора задач
        """
        serializer = CalendarTaskSerializer(instance=self.task)
        expected = {'id', 'type', 'title', 'description', 'deadline', 'status', 'created_by', 'assigned_to', 'team',
                    'is_past', 'time', 'created_at', 'updated_at'}
        assert set(serializer.data.keys()) == expected

    def test_task_serializer_correct_data(self):
        """
        Тест на корректное отображение данных задач
        """
        serializer = CalendarTaskSerializer(instance=self.task)
        assert serializer.data['type'] == 'task'
        assert serializer.data['title'] == self.task.title
        assert serializer.data['status'] == self.task.status
        assert serializer.data['time'] == self.task.deadline
        assert not serializer.data['is_past']

    def test_task_serializer_is_past_true(self):
        """
        Тест на is_past для прошедшей задачи
        """
        with freeze_time(timezone.now() - timedelta(days=2)):
            self.task.deadline = timezone.now() + timedelta(days=1)
            self.task.save()
        serializer = CalendarTaskSerializer(instance=self.task)
        assert serializer.data['is_past']


@pytest.mark.serializers
@pytest.mark.django_db
class TestCalendarMeetingSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, admin_user_data, create_superuser, user_data, create_user, meeting_data, create_meeting):
        self.admin = create_superuser(**admin_user_data)
        self.user = create_user(**user_data)
        self.meeting = create_meeting(creator=self.admin, **meeting_data)
        self.meeting.members.add(self.user)

    def test_meeting_serializer_fields(self):
        """
        Тест на отображение полей сериализатора встреч
        """
        serializer = CalendarMeetingSerializer(instance=self.meeting)
        expected = {'id', 'type', 'topic', 'date', 'start_time', 'end_time', 'creator', 'members', 'full_start_time',
                    'full_end_time', 'is_past', 'time'}
        assert set(serializer.data.keys()) == expected

    def test_meeting_serializer_correct_data(self):
        """
        Тест на корректное отображение данных встречи
        """
        serializer = CalendarMeetingSerializer(instance=self.meeting)
        assert serializer.data['type'] == 'meeting'
        assert serializer.data['topic'] == self.meeting.topic
        assert serializer.data['time'] == self.meeting.full_start_time
        assert not serializer.data['is_past']

    def test_meeting_serializer_is_past_true(self):
        """
        Тест на is_past для прошедшей встречи
        """
        with freeze_time(timezone.now() - timedelta(days=2)):
            self.meeting.date = timezone.now() + timedelta(days=1)
            self.meeting.save()
        serializer = CalendarMeetingSerializer(instance=self.meeting)
        assert serializer.data['is_past']
