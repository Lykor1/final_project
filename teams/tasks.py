import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags

from .models import Team

logger = logging.getLogger(__name__)


@shared_task
def notify_user_team_change(user_email, team_name, action):
    if action not in ('added', 'removed'):
        logger.error(f'Неверный action в notify_user_team_change: {action}')
        return
    if action == 'added':
        subject = 'Вы добавлены в команду'
        html_text = f"""<html>
        <body>
        <h2>Вы добавлены в команду</h2>
        <p>Здравствуйте!</p>
        <p>Вы были добавлены в команду <strong>{team_name}</strong>.</p>
        <p>Теперь вы можете видеть задачи и участвовать в работе команды.</p>
        <p>С наилучшими пожеланиями,<br>Система управления бизнесом</p>
        </body>
        </html>"""
    else:
        subject = 'removed'
        html_text = f"""<html>
        <body>
        <h2>Вы удалены из команды</h2>
        <p>Здравствуйте!</p>
        <p>Вы были удалены из команды <strong>{team_name}</strong>.</p>
        <p>Доступ к задачам и материалам этой команды для вас закрыт.</p>
        <p>С уважением,<br>Система управления бизнесом</p>
        </body>
        </html>"""
    text = strip_tags(html_text)
    try:
        send_mail(
            subject=subject,
            message=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
            html_message=html_text,
        )
        logger.info(f'Уведомление о {action} в команду "{team_name}" отправлено на {user_email}')
    except Exception as e:
        logger.exception(f'Ошибка отправки уведомления о {action} в команду на {user_email}: {str(e)}')
