from rest_framework import serializers
from rest_framework.renderers import JSONRenderer


from .models import AutoNumbers


class AutoNumbersSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoNumbers
        fields = "__all__"

        
