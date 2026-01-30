from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied, ValidationError

from tasks.models import Task


class CanDeleteEvaluationPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.task.created_by != request.user:
            raise PermissionDenied({'task': 'Удалять оценки может лишь создатель задачи'})
        return True


class CanCreateEvaluationPermission(BasePermission):
    def has_permission(self, request, view):
        task_id = view.kwargs.get('task_id')
        task = get_object_or_404(Task, pk=task_id)
        if task.created_by != request.user:
            raise PermissionDenied({'task': 'Ставить оценки может лишь создатель задачи'})
        if task.status != Task.Status.DONE:
            raise ValidationError({'task': 'Ставить оценку можно только для выполненной задачи'})
        return True
