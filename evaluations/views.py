from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404

from tasks.models import Task
from .models import Evaluation
from .serializers import EvaluationCreateSerializer
from .services import EvaluationService



class EvaluationCreateView(CreateAPIView):
    """
    Добавление оценки
    """
    permission_classes = (IsAdminUser,)
    serializer_class = EvaluationCreateSerializer

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs['task_id'])
        user = self.request.user
        EvaluationService.check_create_evaluation_permission(task=task, current_user=user)
        serializer.save(task=task)
