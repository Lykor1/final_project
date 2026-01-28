from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime

User = get_user_model()


def get_full_datetime(date, time):
    return timezone.make_aware(datetime.combine(date, time))


class Meeting(models.Model):
    topic = models.CharField(max_length=100, verbose_name='Тема встречи')
    date = models.DateField(verbose_name='Дата встречи')
    start_time = models.TimeField(verbose_name='Время начала встречи')
    end_time = models.TimeField(verbose_name='Время окончания встречи')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True, related_name='meetings',
                                verbose_name='Создатель встречи')
    members = models.ManyToManyField(User, related_name='meeting_members', verbose_name='Участники встречи')
    reminder_1hour_sent = models.BooleanField(default=False, verbose_name='Напоминание за час отправлено')

    class Meta:
        verbose_name = 'Встреча'
        verbose_name_plural = 'Встречи'
        ordering = ['creator', 'date']

    def __str__(self):
        return f'{self.topic} ({self.date} {self.start_time} - {self.end_time})'

    @property
    def full_start_time(self):
        return get_full_datetime(self.date, self.start_time)

    @property
    def full_end_time(self):
        return get_full_datetime(self.date, self.end_time)

    def clean(self):
        super().clean()
        now = timezone.now()
        start_dt = self.full_start_time
        end_dt = self.full_end_time
        if start_dt < now:
            raise ValidationError({'start_time': 'Время начала встречи не может быть в прошлом'})
        if end_dt <= start_dt:
            raise ValidationError({'end_time': 'Время окончания встречи должно быть позже времени начала'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
