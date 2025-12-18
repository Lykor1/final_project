from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Team

User = get_user_model()


class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('name', 'description')

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError('Название должно содержать минимум 3 символа')
        return value


class TeamAddUserSerializer(serializers.Serializer):
    user_email = serializers.EmailField(help_text='Email пользователя', required=True)

    def validate_user_email(self, value):
        return value.lower().strip()
