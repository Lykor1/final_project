from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Team
from users.serializers import UserDetailSerializer

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


class TeamUpdateUserRoleSerializer(TeamAddUserSerializer):
    user_email = serializers.EmailField(help_text='Email пользователя', required=True)
    user_role = serializers.ChoiceField(choices=User.Role.choices, default=User.Role.USER,
                                        help_text='Роль пользователя')


class MembersSerializer(UserDetailSerializer):
    class Meta(UserDetailSerializer.Meta):
        fields = (
            'email',
            'full_name',
            'birthday',
            'age',
            'role',
            'created_at'
        )
        read_only_fields = fields


class TeamDetailSerializer(serializers.ModelSerializer):
    creator = MembersSerializer(read_only=True)
    members = MembersSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ('name', 'description', 'creator', 'members')
        read_only_fields = fields
