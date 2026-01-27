import logging
from celery import shared_task
from django.core.mail import send_mail
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
