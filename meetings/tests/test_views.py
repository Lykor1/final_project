from datetime import time
import pytest
from django.urls import reverse

from meetings.models import Meeting


@pytest.mark.views
@pytest.mark.django_db
class TestMeetingCreateView:
    @pytest.fixture(autouse=True)
    def setup(self, admin_user_data, create_superuser, create_user, user_data, meeting_data, client):
        self.admin = create_superuser(**admin_user_data)
        self.user1 = create_user(**user_data[0])
        self.user2 = create_user(**user_data[1])
        self.meet_data = meeting_data
        self.url = reverse('meetings:create')
        self.client = client

    def test_create_meeting_success(self):
        """
        Тест на успешное создание встречи
        """
        self.client.force_authenticate(self.admin)
        self.meet_data.update({'members': [self.user1.email, self.user2.email]})
        response = self.client.post(self.url, data=self.meet_data)
        assert response.status_code == 201
        meeting = Meeting.objects.first()
        members_emails = {u.email for u in meeting.members.all()}
        assert self.admin.email in members_emails
        assert self.user1.email in members_emails
        assert self.user2.email in members_emails

    def test_create_meeting_not_admin(self):
        """
        Тест на создание встречи обычным пользователем
        """
        self.client.force_authenticate(self.user1)
        self.meet_data.update({'members': [self.user2.email]})
        response = self.client.post(self.url, data=self.meet_data)
        assert response.status_code == 403

    def test_create_meeting_unauthenticated_user(self):
        """
        Тест на создание встречи анонимным пользователем
        """
        self.meet_data.update({'members': [self.user1.email, self.user2.email]})
        response = self.client.post(self.url, data=self.meet_data)
        assert response.status_code == 401