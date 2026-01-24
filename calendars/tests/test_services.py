from datetime import timedelta, time, datetime
import pytest
from django.utils import timezone
from freezegun import freeze_time

from calendars.services import CalendarService


@pytest.mark.services
@pytest.mark.django_db
class TestGetCalendarData:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, team_data, create_team, user_data, create_user, task_data,
              create_task, create_meeting, meeting_data):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.user = create_user(team=self.team, **user_data)
        self.task_future = create_task(created_by=self.admin, team=self.team, assigned_to=self.user, **task_data)
        self.meeting_future = create_meeting(creator=self.admin, **meeting_data)
        self.meeting_future.members.add(self.user)
        with freeze_time(timezone.now() - timedelta(days=2)):
            self.task_past = create_task(
                title='past task',
                deadline=timezone.make_aware(
                    datetime.combine(timezone.now() + timezone.timedelta(days=1), time(11, 0))),
                created_by=self.admin,
                team=self.team,
                assigned_to=self.user,
            )
            self.meeting_past = create_meeting(
                creator=self.admin,
                topic='past meetings',
                date=timezone.now().date() + timedelta(days=1),
                start_time=meeting_data['start_time'],
                end_time=meeting_data['end_time'],
            )
            self.meeting_past.members.add(self.user)

    def test_get_calendar_data_single_day_success(self):
        """
        Тест на получение данных календаря за один день
        """
        future_date_str = (timezone.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
        data = CalendarService.get_calendar_data(user=self.user, date_str=future_date_str)
        assert data['period'] == future_date_str
        assert data['count'] == 2
        assert data['events'][0]['type'] == 'meetings'
        assert not data['events'][0]['is_past']

    def test_get_calendar_data_range_success(self):
        """
        Тест на получение данных календаря в диапазоне
        """
        start_str = (timezone.now().date() - timedelta(days=1)).strftime('%Y-%m-%d')
        end_str = (timezone.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
        data = CalendarService.get_calendar_data(user=self.user, start_str=start_str, end_str=end_str)
        assert data['period'] == f'{start_str} - {end_str}'
        assert data['count'] == 4
        times = [event['time'] for event in data['events']]
        assert times == sorted(times)

    @pytest.mark.parametrize(
        'date_str, start_str, end_str',
        [
            ('2026-01-01', '2026-01-01', '2026-01-02'),
            ('2026-01-01', '2026-01-01', None),
            (None, '2026-01-01', None),
            (None, None, '2026-01-01'),
            ('invalid_data', None, None),
            (None, 'invalid_data', '2026-01-01'),
            (None, '2026-01-01', 'invalid_data'),
        ]
    )
    def test_get_calendar_data_invalid_params(self, date_str, start_str, end_str):
        """
        Тест на неверные параметры
        """
        with pytest.raises(ValueError):
            CalendarService.get_calendar_data(user=self.user, date_str=date_str, start_str=start_str, end_str=end_str)

    def test_get_calendar_data_no_events(self):
        """
        Тест на отсутствие событий в период
        """
        far_future_start = (timezone.now().date() + timedelta(days=10)).strftime('%Y-%m-%d')
        far_future_end = (timezone.now().date() + timedelta(days=20)).strftime('%Y-%m-%d')
        data = CalendarService.get_calendar_data(user=self.user, start_str=far_future_start, end_str=far_future_end)
        assert data['count'] == 0
        assert data['events'] == []
