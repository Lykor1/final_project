from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .services import CalendarService


class CalendarListView(APIView):
    """
    Получение событий в календаре
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        date_str = request.query_params.get('date')
        start_str = request.query_params.get('start')
        end_str = request.query_params.get('end')
        try:
            data = CalendarService.get_calendar_data(
                user=user,
                date_str=date_str,
                start_str=start_str,
                end_str=end_str,
            )
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
