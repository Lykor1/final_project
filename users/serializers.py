from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'birthday')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Пароли не совпадают'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    team_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    average_rank = serializers.FloatField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'full_name',
            'birthday',
            'age',
            'role',
            'team_name',
            'average_rank',
            'created_at'
        )
        read_only_fields = fields

    def get_team_name(self, obj):
        if not obj.team:
            return None
        return obj.team.name

    def get_age(self, obj):
        if not obj.birthday:
            return None
        return obj.get_age

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip()


class UserListSerializer(UserDetailSerializer):
    class Meta(UserDetailSerializer.Meta):
        fields = (
            'id',
            'email',
            'full_name',
            'birthday',
            'age',
            'role',
            'team_name',
            'created_at'
        )
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'birthday')
        extra_kwargs = {
            'first_name': {
                'required': True,
                'min_length': 2,
            },
            'last_name': {
                'required': True,
                'min_length': 2,
            },
        }
