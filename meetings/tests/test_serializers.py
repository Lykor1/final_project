from datetime import time
import pytest
from django.core.exceptions import ValidationError
from datetime import date, timedelta

from meetings.models import Meeting
from meetings.serializers import MeetingCreateSerializer, MeetingMembersSerializer, MeetingListSerializer


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
            'end_time': time(9, 0),
            'members': []
        })
        serializer = MeetingCreateSerializer(data=self.meet_data)
        serializer.is_valid(raise_exception=True)
        with pytest.raises(ValidationError):
            serializer.save(creator=self.admin)


@pytest.mark.serializers
@pytest.mark.django_db
class TestMeetingMembersSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, create_user, user_data, create_superuser, admin_user_data, team_data, create_team):
        admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=admin, **team_data)
        user_data[0].update({'birthday': date.today().replace(year=date.today().year - 25), 'team': self.team})
        self.user = create_user(**user_data[0])

    def test_list_members_success(self):
        """
        Тест на успешное отображение участников встречи
        """
        serializer = MeetingMembersSerializer(instance=self.user)
        expected_fields = {'email', 'full_name', 'age', 'role', 'team_name'}
        assert set(serializer.data.keys()) == expected_fields
        assert serializer.data['email'] == self.user.email

    @pytest.mark.parametrize(
        'birthday, expected',
        [
            (True, 25),
            (False, None),
        ]
    )
    def test_get_age(self, birthday, expected):
        """
        Тест на get_age
        """
        if not birthday:
            self.user.birthday = None
        serializer = MeetingMembersSerializer(instance=self.user)
        assert serializer.data['age'] == expected

    @pytest.mark.parametrize(
        'team_bool, expected',
        [
            (True, 'test_team'),
            (False, None),
        ]
    )
    def test_get_team_name(self, team_bool, expected):
        """
        Тест на get_team_name
        """
        if not team_bool:
            self.user.team = None
        serializer = MeetingMembersSerializer(instance=self.user)
        assert serializer.data['team_name'] == expected

    @pytest.mark.parametrize(
        'f_name, l_name, expected',
        [
            ('first', 'test', 'first test'),
            (' Second', 'test ', 'Second test'),
            ('third ', ' test', 'third test'),
        ]
    )
    def test_get_full_name(self, f_name, l_name, expected):
        """
        Тест на get_full_name
        """
        self.user.first_name = f_name
        self.user.last_name = l_name
        serializer = MeetingMembersSerializer(instance=self.user)
        assert serializer.data['full_name'] == expected


@pytest.mark.serializers
@pytest.mark.django_db
class TestMeetingListSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, create_user, user_data, admin_user_data, create_superuser, meeting_data):
        self.users = []
        for u in user_data:
            self.users.append(create_user(**u))
        self.admin = create_superuser(**admin_user_data)
        self.meet = Meeting.objects.create(creator=self.admin, **meeting_data)
        self.meet.members.add(*self.users)

    @pytest.fixture
    def create_serializer(self):
        return MeetingListSerializer(instance=self.meet)

    def test_list_meetings_success_fields(self, create_serializer):
        """
        Тест на правильное отображение полей
        """
        serializer = create_serializer
        expected_keys = {'topic', 'date', 'start_time', 'end_time', 'creator', 'members'}
        assert set(serializer.data.keys()) == expected_keys

    def test_list_meeting_data(self, create_serializer):
        """
        Тест на правильное отображение данных о встрече
        """
        serializer = create_serializer
        assert serializer.data['topic'] == self.meet.topic
        assert serializer.data['date'] == str(self.meet.date)
        assert serializer.data['creator'] == f'{self.admin.first_name.strip()} {self.admin.last_name.strip()}'

    def test_list_meeting_members_data(self, create_serializer):
        """
        Тест на правильное отображение данных об участниках
        """
        serializer = create_serializer
        members_data = serializer.data['members']
        assert len(members_data) == len(self.users)
        emails = {m['email'] for m in members_data}
        expected = {user.email for user in self.users}
        assert emails == expected
