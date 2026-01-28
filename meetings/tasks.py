import logging
from datetime import timedelta
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.utils import timezone

from .models import Meeting

logger = logging.getLogger(__name__)


@shared_task
def send_meeting_reminders():
    now = timezone.now()
    window_start = now + timedelta(minutes=50)
    window_end = now + timedelta(minutes=70)
    upcoming = Meeting.objects.filter(
        reminder_1hour_sent=False,
        date__range=(window_start.date(), window_end.date()),
    ).prefetch_related('members', 'creator')
    candidates = []
    for meeting in upcoming:
        start_dt = meeting.full_start_time
        if window_start <= start_dt <= window_end:
            candidates.append(meeting)
    if not candidates:
        logger.info('Нет встреч для отправки уведомлений')
        return
    for meeting in candidates:
        try:
            participants = set(meeting.members.all())
            participants.add(meeting.creator)
            emails = [u.email for u in participants if u.email]
            if not emails:
                continue
            subject = f'Напоминание: встреча "{meeting.topic}"'
            html_body = f"""<html>
            <body>
            <h2>Напоминание о встрече</h2>
            <p>Здравствуйте!</p>
            <p>Встреча <strong>{meeting.topic}</strong> начнётся через ~1 час:</p>
            <ul>
            <li><strong>Тема:</strong> {meeting.topic}</li>
            <li><strong>Дата:</strong> {meeting.date.strftime('%d.%m.%Y')}</li>
            <li><strong>Время:</strong> {meeting.start_time.strftime('%H:%M')} – {meeting.end_time.strftime('%H:%M')}</li>
            <li><strong>Создатель:</strong> {meeting.creator.email} ({meeting.creator.last_name} {meeting.creator.first_name})</li>
            <li><strong>Участники:</strong> {', '.join(u.email for u in meeting.members.all())}</li>
            </ul>
            <p>Будьте на связи!</p>
            <p>С уважением,<br>Система управления бизнесом.</p>
            </body>
            </html>"""
            text_body = strip_tags(html_body)
            send_mail(
                subject=subject,
                message=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=emails,
                fail_silently=False,
                html_message=html_body,
            )
            meeting.reminder_1hour_sent = True
            meeting.save(update_fields=['reminder_1hour_sent'])
            logger.info(f'Напоминание о встрече "{meeting.topic}" отправлено {len(emails)} участникам')
        except Exception as e:
            logger.exception(f'Ошибка отправки напоминания о встрече {meeting.topic}: {str(e)}')
