from rest_framework import serializers
from .models import LogAnalytics, LogItems

class LogAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogItems
        fields = "__all__"
