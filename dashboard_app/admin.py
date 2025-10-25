from django.contrib import admin
from .models import LogAnalytics, LogItems, LogEntry, LogSummary, RawItems

admin.site.register(LogAnalytics)
admin.site.register(LogItems)
admin.site.register(LogEntry)
admin.site.register(LogSummary)
admin.site.register(RawItems)
