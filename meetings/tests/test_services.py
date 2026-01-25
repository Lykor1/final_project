from datetime import time, timedelta
import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from freezegun import freeze_time

from meetings.models import Meeting
from meetings.services import MeetingService


@pytest.mark.services
@pytest.mark.django_db
class TestCreateMeeting:
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
        meeting = MeetingService.create_meeting(
            creator=self.admin,
            topic=self.meet_data['topic'],
            date=self.meet_data['date'],
            start_time=self.meet_data['start_time'],
            end_time=self.meet_data['end_time'],
            members=[self.user1, self.user2]
        )
        member_emails = {u.email for u in meeting.members.all()}
        assert member_emails == {self.admin.email, self.user1.email, self.user2.email}
        assert meeting.creator == self.admin
        assert meeting.topic == self.meet_data['topic']

    def test_create_meeting_conflict_creator(self):
        """
        Тест на конфликт создателя при создании встречи
        """
        MeetingService.create_meeting(
            creator=self.admin,
            topic=self.meet_data['topic'],
            date=self.meet_data['date'],
            start_time=self.meet_data['start_time'],
            end_time=self.meet_data['end_time'],
            members=[]
        )
        with pytest.raises(ValidationError) as e:
            MeetingService.create_meeting(
                creator=self.admin,
                topic=self.meet_data['topic'],
                date=self.meet_data['date'],
                start_time=time(10, 30),
                end_time=time(11, 30),
                members=[]
            )
        assert 'members' in str(e.value)

    def test_create_meeting_conflict_member(self, create_superuser, admin_user_data):
        """
        Тест на конфликт участника при создании встречи
        """
        new_admin = create_superuser(
            email='newadmin@example.com',
            password=admin_user_data['password'],
            first_name=admin_user_data['first_name'],
            last_name=admin_user_data['last_name']
        )
        MeetingService.create_meeting(
            creator=self.admin,
            topic=self.meet_data['topic'],
            date=self.meet_data['date'],
            start_time=self.meet_data['start_time'],
            end_time=self.meet_data['end_time'],
            members=[self.user1]
        )
        with pytest.raises(ValidationError) as e:
            MeetingService.create_meeting(
                creator=new_admin,
                topic=self.meet_data['topic'],
                date=self.meet_data['date'],
                start_time=time(10, 30),
                end_time=time(11, 30),
                members=[self.user1]
            )
        assert self.user1.email in str(e.value)


@pytest.mark.services
@pytest.mark.django_db
class TestUpdateMeeting:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, create_user, user_data, meeting_data):
        self.admin = create_superuser(**admin_user_data)
        self.user = create_user(**user_data[0])
        self.meet = Meeting.objects.create(creator=self.admin, **meeting_data)
        self.new_data = {
            'topic': 'new topic',
            'date': timezone.now().date() + timezone.timedelta(days=3),
            'start_time': time(11, 0),
            'end_time': time(12, 0),
            'members': [self.user]
        }

    def test_update_meeting_success(self):
        """
        Тест на успешное обновление данных сервисом
        """
        new_meet = MeetingService.update_meeting(
            meeting=self.meet,
            creator=self.admin,
            topic=self.new_data['topic'],
            date=self.new_data['date'],
            start_time=self.new_data['start_time'],
            end_time=self.new_data['end_time'],
            members=self.new_data['members']
        )
        new_meet.refresh_from_db()
        assert new_meet.topic == self.new_data['topic']
        assert new_meet.date == self.new_data['date']

    def test_update_completed_meeting(self, meeting_data):
        """
        Тест на обновление прошедшей встречи
        """
        with freeze_time(timezone.now() - timedelta(days=3)):
            completed_meet = Meeting.objects.create(
                topic=meeting_data['topic'],
                date=timezone.now().date(),
                start_time=(timezone.now() + timedelta(hours=5)).time(),
                end_time=(timezone.now() + timedelta(hours=6)).time(),
                creator=self.admin,
            )
        with pytest.raises(ValidationError) as e:
            MeetingService.update_meeting(
                meeting=completed_meet,
                creator=self.admin,
                topic=self.new_data['topic'],
                date=self.new_data['date'],
                start_time=self.new_data['start_time'],
                end_time=self.new_data['end_time'],
                members=self.new_data['members']
            )
        assert 'Нельзя редактировать прошедшую встречу' in str(e.value)

    def test_update_meeting_conflict_members(self, meeting_data, admin_user_data, create_superuser):
        """
        Тест на обновление встречи с конфликтом участника
        """
        new_admin = create_superuser(
            email='newadmin@example.com',
            password=admin_user_data['password'],
            first_name=admin_user_data['first_name'],
            last_name=admin_user_data['last_name']
        )
        another_meet = Meeting.objects.create(
            topic=self.new_data['topic'],
            date=self.new_data['date'],
            start_time=self.new_data['start_time'],
            end_time=self.new_data['end_time'],
            creator=new_admin
        )
        another_meet.members.set([self.user])
        with pytest.raises(ValidationError) as e:
            MeetingService.update_meeting(
                meeting=self.meet,
                creator=self.admin,
                topic=self.new_data['topic'],
                date=self.new_data['date'],
                start_time=self.new_data['start_time'],
                end_time=self.new_data['end_time'],
                members=self.new_data['members']
            )
        assert 'Следующие пользователи уже участвуют в другой встрече' in str(e.value)
