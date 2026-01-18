from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q

from tasks.models import Task
from meetings.models import Meeting
from .serializers import CalendarTaskSerializer, CalendarMeetingSerializer


class CalendarService:
    @staticmethod
    def get_calendar_data(user, date_str=None, start_str=None, end_str=None):
        """
        Возвращает данные календаря за день или диапазон дат
        """
        if date_str and (start_str or end_str):
            raise ValueError('Используйте либо date, либо start+end')
        try:
            if date_str:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                start_dt = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
                end_dt = start_dt + timedelta(days=1)
                period_label = target_date.strftime('%Y-%m-%d')
            else:
                if not start_str or not end_str:
                    raise ValueError('Для диапазона нужны start и end')
                start_dt = timezone.make_aware(datetime.strptime(start_str, '%Y-%m-%d'))
                end_dt = timezone.make_aware(datetime.strptime(end_str, '%Y-%m-%d')) + timedelta(days=1)
                period_label = f'{start_str} - {end_str}'
            tasks_qs = Task.objects.filter(
                Q(assigned_to=user) | Q(created_by=user),
                deadline__gte=start_dt,
                deadline__lt=end_dt,
            ).select_related('created_by', 'assigned_to', 'team').order_by('deadline')
            meeting_qs = Meeting.objects.filter(
                members=user,
                date__gte=start_dt.date(),
                date__lt=end_dt.date()
            ).prefetch_related('members').order_by('start_time')
            tasks_data = CalendarTaskSerializer(tasks_qs, many=True).data
            meeting_data = CalendarMeetingSerializer(meeting_qs, many=True).data
            events = tasks_data + meeting_data
            events.sort(key=lambda x: x['time'])
            return {
                'period': period_label,
                'count': len(events),
                'events': events,
            }
        except ValueError as e:
            raise ValueError(f'Неверный формат даты: {str(e)}')
