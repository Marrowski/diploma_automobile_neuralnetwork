from rest_framework import serializers
from rest_framework.renderers import JSONRenderer


from .models import AutoNumbers


class AutoNumbersSerializer(serializers.Serializer):
    numbers = serializers.CharField(max_length=8)
    is_allowed = serializers.BooleanField(default=False)
    time_create = serializers.DateTimeField(read_only=True)
    id = serializers.IntegerField()
    




        
    