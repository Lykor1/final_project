from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название команды')
    description = models.TextField(blank=True, verbose_name='Описание команды')
    creator = models.ForeignKey('users.UserWithEmail', on_delete=models.PROTECT, related_name='created_teams',
                                verbose_name='Создатель команды')

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'
        ordering = ('name', 'creator')

    def __str__(self):
        return self.name
