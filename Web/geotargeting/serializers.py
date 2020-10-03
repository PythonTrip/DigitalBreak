from rest_framework import serializers
from .models import Point


class PointSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    central_point = serializers.FloatField()
    radius_area = serializers.FloatField()

    def create(self, validated_data):
        return Point.objects.create(**validated_data)
