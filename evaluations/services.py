from rest_framework.exceptions import ValidationError, PermissionDenied

from tasks.models import Task

class EvaluationService:
    @staticmethod
    def check_create_evaluation_permission(*, task, current_user):
        if task.created_by != current_user:
            raise PermissionDenied({'task': 'Ставить оценки может лишь создатель задачи'})
        if task.status != Task.Status.DONE:
            raise ValidationError({'task': 'Ставить оценку можно только для выполненной задачи'})