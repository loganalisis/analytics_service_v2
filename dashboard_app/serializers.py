from rest_framework import serializers
from .models import LogAnalytics, LogItems, RawItems

class LogAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawItems
        fields = "__all__"
