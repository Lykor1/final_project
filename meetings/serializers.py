from rest_framework import serializers
from django.contrib.auth import get_user_model

from meetings.models import Meeting

User = get_user_model()


class MeetingSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True,
        slug_field='email',
        queryset=User.objects.all()
    )

    class Meta:
        model = Meeting
        fields = ('topic', 'date', 'start_time', 'end_time', 'members')
