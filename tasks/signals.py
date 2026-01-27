from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Task
from .tasks import notify_assigned_to

_old_assigned = {}


@receiver(pre_save, sender=Task)
def remember_old_assigned_to(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Task.objects.only('assigned_to').get(pk=instance.pk)
            _old_assigned[instance.pk] = old.assigned_to
        except Task.DoesNotExist:
            _old_assigned[instance.pk] = None


@receiver(post_save, sender=Task)
def send_notification_on_assignment(sender, instance, created, **kwargs):
    if instance.assigned_to:
        old_assigned = _old_assigned.pop(instance.pk, None)
        if created or old_assigned != instance.assigned_to:
            notify_assigned_to.delay(instance.pk)
