from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from .serializers import UserRegisterSerializer

User = get_user_model()


class UserRegisterView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()
