from rest_framework import serializers

from .models import Evaluation


class EvaluationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = ('rank',)
