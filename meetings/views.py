from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Meeting
from .serializers import MeetingCreateSerializer, MeetingListSerializer
from .services import MeetingService


class MeetingCreateView(CreateAPIView):
    """
    Создание встречи
    """
    permission_classes = (IsAdminUser,)
    serializer_class = MeetingCreateSerializer

    def perform_create(self, serializer):
        try:
            meeting = MeetingService.create_meeting(
                creator=self.request.user,
                **serializer.validated_data
            )
            serializer.instance = meeting
        except ValidationError as e:
            raise DRFValidationError(e.message_dict)


class MeetingDeleteView(DestroyAPIView):
    """
    Удаление встречи
    """
    permission_classes = (IsAdminUser,)
    queryset = Meeting.objects.all()

    def get_queryset(self):
        return Meeting.objects.filter(creator=self.request.user)


class MeetingListView(ListAPIView):
    """
    Просмотр встреч
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = MeetingListSerializer

    def get_queryset(self):
        return Meeting.objects.filter(
            members=self.request.user
        ).select_related(
            'creator'
        ).prefetch_related(
            'members'
        ).distinct().order_by(
            'date', 'start_time'
        )
