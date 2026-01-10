from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from meetings.models import Meeting


def has_time_conflict(*, user, date, start_time, end_time):
    return Meeting.objects.filter(
        date=date
    ).filter(
        Q(start_time__lt=end_time) &
        Q(end_time__gt=start_time)
    ).filter(
        Q(creator=user) | Q(members=user)
    ).exists()


class MeetingService:
    @staticmethod
    @transaction.atomic
    def create_meeting(*, creator, topic, date, start_time, end_time, members):
        """
        Функция для создания встречи
        """
        members = set(members or [])
        members.add(creator)
        user_ids = [u.id for u in members]
        conflicts = Meeting.objects.filter(
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).filter(
            Q(creator__in=user_ids) | Q(members__in=user_ids)
        ).distinct().prefetch_related('members')
        conflicted_users = set()
        for meeting in conflicts:
            if meeting.creator_id in user_ids:
                conflicted_users.add(meeting.creator)
            conflicted_users.update(
                u for u in meeting.members.all() if u.id in user_ids
            )
        if conflicted_users:
            emails = ', '.join(u.email for u in conflicted_users)
            raise ValidationError({'members': f'Следующие пользователи уже участвуют в другой встрече: {emails}'})

        meeting = Meeting.objects.create(
            topic=topic,
            date=date,
            start_time=start_time,
            end_time=end_time,
            creator=creator,
        )
        meeting.members.set(members)
        return meeting
