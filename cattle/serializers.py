from rest_framework import serializers
from .models import Cattle, HealthCheck


class HealthCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCheck
        fields = '__all__'


class CattleSerializer(serializers.ModelSerializer):
    healthchecks = HealthCheckSerializer(many=True, read_only=True)

    class Meta:
        model = Cattle
        fields = '__all__'
