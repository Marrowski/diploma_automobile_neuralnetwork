from rest_framework import serializers
from rest_framework.renderers import JSONRenderer


from .models import AutoNumbers, Category


class AutoNumbersSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault)
    class Meta:
        model = AutoNumbers
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
