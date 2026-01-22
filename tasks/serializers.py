from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Task, validate_future_date, Comment

User = get_user_model()


class TaskCreateSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SlugRelatedField(
        slug_field='email',
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = ('title', 'description', 'deadline', 'status', 'assigned_to')

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError('Название задачи должно содержать минимум 3 символа')
        return value

    def validate_deadline(self, value):
        return validate_future_date(value)

    def validate(self, attrs):
        status = attrs.get('status')
        assigned_to = attrs.get('assigned_to')
        if status in [Task.Status.IN_PROGRESS, Task.Status.DONE] and assigned_to is None:
            raise ValidationError(
                {'status': "Нельзя установить статус задачи 'В работе' или 'Выполнена' без исполнителя"}
            )
        return attrs


class TaskUpdateSerializer(TaskCreateSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance and self.instance.status == Task.Status.DONE:
            if 'deadline' in attrs:
                raise serializers.ValidationError({'deadline': 'Нельзя изменять срок исполнения у выполненной задачи'})
            if 'assigned_to' in attrs:
                raise serializers.ValidationError({'assigned_to': 'Нельзя изменить исполнителя у выполненной задачи'})
        return attrs


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text',)

    def validate_text(self, value):
        return value.strip()


class CommentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('author', 'text')
        read_only_fields = fields


class TaskListUserSerializer(serializers.ModelSerializer):
    comments = CommentListSerializer(read_only=True, many=True, source='tasks')
    rank = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = Task
        fields = ('title', 'description', 'deadline', 'status', 'created_by', 'rank', 'created_at', 'updated_at',
                  'comments')
        read_only_fields = fields


class TaskListAdminSerializer(serializers.ModelSerializer):
    comments = CommentListSerializer(read_only=True, many=True, source='tasks')

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'deadline', 'status', 'assigned_to', 'team', 'created_at', 'updated_at',
                  'comments')
        read_only_fields = fields
