from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from teams.models import Team

User = get_user_model()


def validate_future_date(value):
    if value and value < timezone.now():
        raise ValidationError("Дата не может быть в прошлом.")
    return value


class Task(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'открытая'
        IN_PROGRESS = 'in_progress', 'в работе'
        DONE = 'done', 'выполнена'

    title = models.CharField(max_length=100, verbose_name='Название задачи')
    description = models.TextField(blank=True, verbose_name='Описание задачи')
    deadline = models.DateTimeField(verbose_name='Срок исполнения')
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN,
                              verbose_name='Статус задачи')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', db_index=True,
                                   verbose_name='Автор задачи')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_tasks', blank=True,
                                    null=True, verbose_name='Исполнитель')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_tasks', verbose_name='Команда')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    reminder_7days_sent = models.BooleanField(default=False, verbose_name='Напоминание за 7 дней отправлено')
    reminder_1day_sent = models.BooleanField(default=False, verbose_name='Напоминание за 1 день отправлено')
    overdue_reminder_last_sent = models.BooleanField(null=True, blank=True, verbose_name='Дата последнего напоминания о проcрочке')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['created_by', '-created_at']

    def clean(self):
        super().clean()
        validate_future_date(self.deadline)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='tasks', verbose_name='Задача')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_authors', db_index=True,
                               verbose_name='Автор')
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at', 'task']

    def __str__(self):
        return f'{self.author}({self.task}): {self.text}'
