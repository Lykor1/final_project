import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


@pytest.mark.views
@pytest.mark.django_db
class TestCalendarListView:
    @pytest.fixture(autouse=True)
    def setup(self, client, admin_user_data, create_superuser, create_team, team_data, create_user, user_data,
              task_data, create_task, create_meeting, meeting_data):
        self.client = client
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.user = create_user(team=self.team, **user_data)
        self.task = create_task(created_by=self.admin, team=self.team, assigned_to=self.user, **task_data)
        self.meeting = create_meeting(creator=self.admin, **meeting_data)
        self.meeting.members.add(self.user)
        self.url = reverse('calendars:calendar')

    def test_calendar_view_single_day_success(self):
        """
        Тест на успешное получение календаря за один день
        """
        self.client.force_authenticate(self.user)
        future_date_str = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.get(self.url, {'date': future_date_str})
        assert response.status_code == 200
        assert response.data['period'] == future_date_str
        assert response.data['count'] == 2

    def test_calendar_view_range_success(self):
        """
        Тест на успешное получение календаря за диапазон дат
        """
        self.client.force_authenticate(self.user)
        start_str = timezone.now().date().strftime('%Y-%m-%d')
        end_str = (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        response = self.client.get(self.url, {'start': start_str, 'end': end_str})
        print(response.data)
        assert response.status_code == 200
        assert response.data['period'] == f'{start_str} - {end_str}'
        assert response.data['count'] == 2

    def test_calendar_view_only_created_by_or_assigned_to(self):
        """
        Тест на получение задачи в календаре только исполнителям и создателям
        """
        self.client.force_authenticate(self.user)
        self.task.assigned_to = None
        self.task.save()
        response = self.client.get(self.url, {'date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')})
        assert response.status_code == 200
        assert response.data['count'] == 1
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.url, {'date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')})
        assert response.status_code == 200
        assert response.data['count'] == 1

    def test_calendar_view_no_events(self):
        """
        Тест на отсутствие событий
        """
        self.client.force_authenticate(self.user)
        far_future_date = (timezone.now().date() + timedelta(days=10)).strftime('%Y-%m-%d')
        response = self.client.get(self.url, {'date': far_future_date})
        assert response.status_code == 200
        assert response.data['count'] == 0
        assert response.data['events'] == []

    def test_calendar_view_unauthenticated(self):
        """
        Тест получение календаря анонимным пользователем
        """
        response = self.client.get(self.url)
        assert response.status_code == 401
