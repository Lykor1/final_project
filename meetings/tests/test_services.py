from datetime import time

import pytest
from rest_framework.exceptions import ValidationError

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
