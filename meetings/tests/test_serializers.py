from datetime import time
import pytest
from django.core.exceptions import ValidationError

from meetings.serializers import MeetingCreateSerializer


@pytest.mark.serializers
@pytest.mark.django_db
class TestMeetingCreateSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, create_user, user_data, meeting_data):
        self.admin = create_superuser(**admin_user_data)
        self.user1 = create_user(**user_data[0])
        self.user2 = create_user(**user_data[1])
        self.meet_data = meeting_data

    def test_create_meeting_success(self):
        """
        Тест на успешное создание встречи
        """
        self.meet_data.update({'members': [self.user1.email, self.user2.email]})
        serializer = MeetingCreateSerializer(data=self.meet_data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['topic'] == self.meet_data['topic']
        assert serializer.validated_data['start_time'] == self.meet_data['start_time']
        members = serializer.validated_data['members']
        assert len(members) == 2
        assert members[0].email == self.user1.email

    def test_create_meeting_invalid_email(self):
        """
        Тест на создание встречи с несуществующим email участника
        """
        self.meet_data.update({'members': ['invalid@example.com']})
        serializer = MeetingCreateSerializer(data=self.meet_data)
        assert not serializer.is_valid()
        assert 'members' in serializer.errors

    def test_create_meeting_members_are_saved(self):
        """
        Тест на успешную работу M2M
        """
        self.meet_data.update({'members': [self.user1.email]})
        serializer = MeetingCreateSerializer(data=self.meet_data)
        serializer.is_valid(raise_exception=True)
        meet = serializer.save(creator=self.admin)
        assert meet.members.count() == 1
        assert meet.members.first().email == self.user1.email

    def test_create_meeting_clean(self):
        """
        Тест на работу clean у модели при сохранении
        """
        self.meet_data.update({
            'end_time': time(9,0),
            'members': []
        })
        serializer = MeetingCreateSerializer(data=self.meet_data)
        serializer.is_valid(raise_exception=True)
        with pytest.raises(ValidationError):
            serializer.save(creator=self.admin)
