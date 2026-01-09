import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from meetings.models import Meeting, get_full_datetime


@pytest.mark.models
@pytest.mark.django_db
class TestMeetingModel:
    """
    - str
    - ordering
    """

    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data):
        self.admin = create_superuser(**admin_user_data)
        self.meeting_data = {
            'topic': 'test topic',
            'date': timezone.now().date() + timezone.timedelta(days=2),
            'start_time': (timezone.now() + timezone.timedelta(hours=5)).time(),
            'end_time': (timezone.now() + timezone.timedelta(hours=6)).time(),
            'creator': self.admin,
        }

    def test_create_meeting(self):
        """
        Тест на успешное создание записи в модели встреч
        """
        meet = Meeting.objects.create(**self.meeting_data)
        meet.members.add(self.admin)
        meet.refresh_from_db()
        assert meet.pk is not None
        assert meet.topic == 'test topic'
        assert meet.date == self.meeting_data['date']
        assert meet.start_time == self.meeting_data['start_time']
        assert meet.end_time == self.meeting_data['end_time']
        assert meet.creator == self.admin
        assert meet.members.count() == 1
        assert self.admin in meet.members.all()

    @pytest.mark.parametrize(
        'field',
        [
            'topic',
            'date',
            'start_time',
            'end_time',
            'creator',
        ]
    )
    def test_meeting_without_required_fields(self, field):
        """
        Тест на создание записи встреч без обязательных полей
        """
        self.meeting_data.pop(field)
        with pytest.raises((ValidationError, TypeError)):
            Meeting.objects.create(**self.meeting_data)

    @pytest.mark.parametrize(
        'date, start_time, end_time, expected',
        [
            (timezone.now().date() - timezone.timedelta(days=2), (timezone.now() + timezone.timedelta(hours=5)).time(),
             (timezone.now() + timezone.timedelta(hours=6)).time(), 'date'),
            (timezone.now().date() + timezone.timedelta(days=2), (timezone.now() - timezone.timedelta(hours=5)).time(),
             (timezone.now() + timezone.timedelta(hours=6)).time(), 'start_time'),
            (timezone.now().date() + timezone.timedelta(days=2), (timezone.now() + timezone.timedelta(hours=5)).time(),
             (timezone.now() - timezone.timedelta(hours=6)).time(), 'end_time'),
        ]
    )
    def test_invalid_date_and_time(self, date, start_time, end_time, expected):
        """
        Тест на создание записи встреч с невалидными датой и временами
        """
        self.meeting_data.update({'date': date, 'start_time': start_time, 'end_time': end_time})
        with pytest.raises(ValidationError) as e:
            Meeting.objects.create(**self.meeting_data)
            assert expected in e

    def test_full_start_time_and_end_time(self):
        """
        Тест на проверку get_full_datetime
        """
        meet = Meeting.objects.create(**self.meeting_data)
        assert meet.full_start_time == get_full_datetime(self.meeting_data['date'], self.meeting_data['start_time'])
        assert meet.full_end_time == get_full_datetime(self.meeting_data['date'], self.meeting_data['end_time'])

    def test_str_representation(self):
        """
        Тест на __str__
        """
        meet = Meeting.objects.create(**self.meeting_data)
        assert str(
            meet
        ) == f'{self.meeting_data["topic"]} ({self.meeting_data["date"]} {self.meeting_data["start_time"]} - {self.meeting_data["end_time"]})'

    def test_default_ordering(self):
        """
        Тест на сортировку
        """
        fields = Meeting._meta.ordering
        assert fields == ['creator', 'date']
