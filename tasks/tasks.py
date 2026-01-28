import logging
from collections import defaultdict
from datetime import timedelta
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.html import strip_tags
from django.conf import settings

from .models import Task

logger = logging.getLogger(__name__)


@shared_task
def notify_assigned_to(task_id):
    try:
        task = Task.objects.select_related('assigned_to', 'created_by', 'team').get(pk=task_id)
        if not task.assigned_to:
            return
        subject = f'Новая задача назначена вам: {task.title}'
        html_message = f"""<html>
        <body>
        <h2>Вам назначена новая задача</h2>
        <p>Здравствуйте, <strong>{task.assigned_to.last_name} {task.assigned_to.first_name}</strong>!</p>
        
        <p><strong>Задача:</strong> {task.title}</p>
        <p><strong>Описание:</strong> {task.description or '---'}</p>
        <p><strong>Срок:</strong> {task.deadline.strftime('%d-%m-%Y %H:%M')}</p>
        <p><strong>Статус:</strong> {task.get_status_display()}</p>
        <p><strong>Команда:</strong> {task.team.name}</p>
        <p><strong>Автор:</strong> {task.created_by.last_name} {task.created_by.first_name}</p>
        <br>
        <p>С наилучшим пожеланиями, <br>Ваша система управления бизнесом</p>
        </body>
        </html>"""
        text_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[task.assigned_to.email],
            fail_silently=False,
            html_message=html_message,
        )
        logger.info(
            'Уведомление отправлено на %s (задача #%d: %s)',
            task.assigned_to.email,
            task.id,
            task.title
        )
    except Task.DoesNotExist:
        logger.warning('Задача #%d не найдена при отправке уведомления', task_id)
    except Exception as e:
        logger.exception(
            'Ошибка при отправке уведомления о задаче #%d: %s',
            task_id,
            str(e)
        )


@shared_task
def send_deadline_reminders():
    now = timezone.now()
    seven_days_window_start = now + timedelta(days=6, hours=12)
    seven_days_window_end = now + timedelta(days=7, hours=12)
    one_day_window_start = now + timedelta(hours=12)
    one_day_window_end = now + timedelta(days=1, hours=12)
    qs = Task.objects.filter(
        status__in=[Task.Status.OPEN, Task.Status.IN_PROGRESS],
        assigned_to__isnull=False,
    ).select_related('assigned_to', 'team', 'created_by')
    notifications = defaultdict(list)
    for task in qs.iterator():
        deadline = task.deadline
        if (
                not task.reminder_7days_sent and
                seven_days_window_start <= deadline <= seven_days_window_end
        ):
            notifications[task.assigned_to.email].append((task, '7days'))
        if (
                not task.reminder_1day_sent and
                one_day_window_start <= deadline <= one_day_window_end
        ):
            notifications[task.assigned_to.email].append((task, '1days'))
        if deadline < now:
            last_sent = task.overdue_reminder_last_sent
            if last_sent is None or (now.date() - last_sent).days >= 1:
                notifications[task.assigned_to.email].append((task, 'overdue'))
    if not notifications:
        logger.info('Нет задач для отправки напоминаний о сроках исполнения')
        return
    for email, items in notifications.items():
        try:
            subject = 'Напоминание: срок исполнения задачи'
            lines = []
            updated_fields = []
            for task, rtype in items:
                if rtype == '7days':
                    lines.append(
                        f'<li>{task.title} - <strong>через ~7 дней</strong> ({task.deadline:%d.%m.%Y %H:%M})</li>')
                    task.reminder_7days_sent = True
                    updated_fields.append('reminder_7days_sent')
                elif rtype == '1days':
                    lines.append(f'<li>{task.title} - <strong>завтра</strong> ({task.deadline:%d.%m.%Y %H:%M})</li>')
                    task.reminder_1day_sent = True
                    updated_fields.append('reminder_1day_sent')
                elif rtype == 'overdue':
                    days_over = (now - task.deadline).days
                    lines.append(f'<li>{task.title} - <strong>просрочена на {days_over} дн.</strong></li>')
                    task.overdue_reminder_last_sent = now.date()
                    updated_fields.append('overdue_reminder_last_sent')
                if updated_fields:
                    task.save(update_fields=updated_fields)
            html_body = """<html>
            <body>
            <h2>Напоминание о сроках исполнения</h2>
            <p>Здравствуйте!</p>
            <p>У вас есть задачи, требующие внимания:</p>
            <ul>""" + "".join(lines) + """""</ul>
            <p>С уважением,<br>Система управления бизнесом.</p>
            </body>
            </html>"""
            text_body = strip_tags(html_body)
            send_mail(
                subject=subject,
                message=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
                html_message=html_body,
            )
            logger.info(f'Отправлены напоминания о дедлайнах на {email} ({len(items)} задач)')
        except Exception as e:
            logger.exception(f'Ошибка при отправке напоминаний о сроках исполнения на {e}')
