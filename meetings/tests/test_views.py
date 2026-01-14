from datetime import time
import pytest
from django.urls import reverse
from django.utils import timezone

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


@pytest.mark.views
@pytest.mark.django_db
class TestMeetingDeleteView:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, create_user, user_data, meeting_data, client):
        self.admin = create_superuser(**admin_user_data)
        self.user = create_user(**user_data[0])
        meet = Meeting.objects.create(creator=self.admin, **meeting_data)
        meet.members.add(self.user)
        self.url = reverse('meetings:delete', kwargs={'pk': meet.pk})
        self.client = client

    def test_delete_meeting_success(self):
        """
        Тест на успешное удаление встречи
        """
        self.client.force_authenticate(self.admin)
        assert Meeting.objects.count() == 1
        response = self.client.delete(self.url)
        assert response.status_code == 204
        assert Meeting.objects.count() == 0

    def test_delete_someone_else_meeting(self, create_superuser, admin_user_data):
        """
        Тест на удаление чужой встречи
        """
        new_admin = create_superuser(
            email='newadmin@example.com',
            password=admin_user_data['password'],
            first_name=admin_user_data['first_name'],
            last_name=admin_user_data['last_name'],
        )
        assert Meeting.objects.count() == 1
        self.client.force_authenticate(new_admin)
        response = self.client.delete(self.url)
        assert response.status_code == 404
        assert Meeting.objects.count() == 1

    def test_delete_meeting_not_found(self):
        """
        Тест на удаление несуществующей встречи
        """
        new_url = reverse('meetings:delete', kwargs={'pk': 999})
        assert Meeting.objects.count() == 1
        self.client.force_authenticate(self.admin)
        response = self.client.delete(new_url)
        assert response.status_code == 404
        assert Meeting.objects.count() == 1

    def test_delete_meeting_not_admin(self):
        """
        Тест на удаление встречи обычным пользователем
        """
        self.client.force_authenticate(self.user)
        assert Meeting.objects.count() == 1
        response = self.client.delete(self.url)
        assert response.status_code == 403
        assert Meeting.objects.count() == 1

    def test_delete_meeting_unauthenticated_user(self):
        """
        Тест на удаление встречи анонимом
        """
        assert Meeting.objects.count() == 1
        response = self.client.delete(self.url)
        assert response.status_code == 401
        assert Meeting.objects.count() == 1


@pytest.mark.views
@pytest.mark.django_db
class TestMeetingListView:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, create_user, user_data, meeting_data, client):
        self.admin = create_superuser(**admin_user_data)
        self.user = create_user(**user_data[0])
        self.meet = Meeting.objects.create(creator=self.admin, **meeting_data)
        self.meet.members.add(self.admin)
        self.client = client
        self.url = reverse('meetings:list')

    def test_list_meeting_success(self):
        """
        Тест на успешное отображение списка встреч
        """
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert self.meet.members.count() == 1
        assert response.data[0]['topic'] == self.meet.topic
        assert response.data[0]['creator'] == f'{self.admin.first_name} {self.admin.last_name}'
        assert response.data[0]['members'][0]['email'] == self.admin.email

    def test_list_without_meeting(self):
        """
        Тест доступ без встреч
        """
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert response.data == []

    def test_list_meeting_unauthenticated_user(self):
        """
        Тест на получение списка встреч анонимным пользователем
        """
        response = self.client.get(self.url)
        assert response.status_code == 401


@pytest.mark.views
@pytest.mark.django_db
class TestMeetingUpdateView:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, create_user, user_data, meeting_data, client):
        self.client = client
        self.admin = create_superuser(**admin_user_data)
        self.user = create_user(**user_data[0])
        self.meet = Meeting.objects.create(creator=self.admin, **meeting_data)
        self.new_data = {
            'topic': 'new topic',
            'date': timezone.now().date() + timezone.timedelta(days=3),
            'start_time': time(11, 0),
            'end_time': time(12, 0),
            'members': [self.user.email]
        }
        self.url = reverse('meetings:update', kwargs={'pk': self.meet.pk})

    def test_update_meeting_success(self):
        """
        Тест на успешное обновление встречи
        """
        self.client.force_authenticate(self.admin)
        response = self.client.put(self.url, data=self.new_data)
        print(response.data)
        assert response.status_code == 200
        self.meet.refresh_from_db()
        assert self.meet.topic == self.new_data['topic']
        assert self.meet.date == self.new_data['date']

    def test_patch_update_meeting(self, meeting_data):
        """
        Тест на частичное обновление встречи
        """
        self.client.force_authenticate(self.admin)
        response = self.client.patch(self.url, data={'topic': self.new_data['topic']})
        assert response.status_code == 200
        self.meet.refresh_from_db()
        assert self.meet.topic == self.new_data['topic']
        assert self.meet.date == meeting_data['date']

    def test_update_someone_else_meeting(self, admin_user_data, create_superuser):
        """
        Тест на обновление чужой встречи
        """
        new_admin = create_superuser(
            email='newadmin@example.com',
            password=admin_user_data['password'],
            first_name=admin_user_data['first_name'],
            last_name=admin_user_data['last_name'],
        )
        self.client.force_authenticate(new_admin)
        response = self.client.put(self.url, data=self.new_data)
        assert response.status_code == 404

    def test_update_non_exist_meeting(self):
        """
        Тест на обновление несуществующей встречи
        """
        new_url = reverse('meetings:update', kwargs={'pk': 999})
        self.client.force_authenticate(self.admin)
        response = self.client.put(new_url, data=self.new_data)
        assert response.status_code == 404

    def test_update_meeting_not_admin(self):
        """
        Тест на обновление встречи обычным пользователем
        """
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url, data=self.new_data)
        assert response.status_code == 403

    def test_update_meeting_unauthenticated_user(self):
        """
        Тест на обновление встречи анонимным пользователем
        """
        response = self.client.put(self.url, data=self.new_data)
        assert response.status_code == 401
