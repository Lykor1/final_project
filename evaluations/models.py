from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from tasks.models import Task


class Evaluation(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, db_index=True, related_name='task_evaluation',
                             verbose_name='Задача')
    rank = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)],
                                            verbose_name='Оценка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата оценки')

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        ordering = ['task']

    def __str__(self):
        return f'{self.task.title} ({self.task.assigned_to}): {self.rank}'

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
