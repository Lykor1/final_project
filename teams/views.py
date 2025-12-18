from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView
)
from rest_framework.permissions import IsAdminUser

from .models import Team
from .serializers import TeamCreateSerializer


class TeamCreateAPIView(CreateAPIView):
    """
    Создание команды админом
    """
    queryset = Team.objects.all()
    serializer_class = TeamCreateSerializer
    permission_classes = (IsAdminUser,)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class TeamDeleteAPIView(DestroyAPIView):
    """
    Удаление команды админом
    """
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        return Team.objects.filter(creator=self.request.user)
