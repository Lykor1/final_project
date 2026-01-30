from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAdminUser

from tasks.models import Task
from .models import Evaluation
from .serializers import EvaluationCreateSerializer
# from .services import EvaluationService
from .permissions import CanDeleteEvaluationPermission, CanCreateEvaluationPermission


class EvaluationCreateView(CreateAPIView):
    """
    Добавление оценки
    """
    permission_classes = (IsAdminUser, CanCreateEvaluationPermission)
    serializer_class = EvaluationCreateSerializer

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs['task_id'])
        # user = self.request.user
        # EvaluationService.check_create_evaluation_permission(task=task, current_user=user)
        serializer.save(task=task)


class EvaluationDeleteView(DestroyAPIView):
    """
    Удаление оценки
    """
    permission_classes = (IsAdminUser, CanDeleteEvaluationPermission)

    def get_object(self):
        task = get_object_or_404(Task, pk=self.kwargs['task_id'])
        # EvaluationService.check_delete_evaluation_permission(task=task, current_user=self.request.user)
        eval = get_object_or_404(Evaluation, task=task)
        self.check_object_permissions(self.request, eval)
        return eval
