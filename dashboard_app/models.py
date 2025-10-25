from django.db import models

class LogAnalytics(models.Model):
    file_name = models.CharField(max_length=255)
    blob_url = models.URLField()
    error_count = models.IntegerField(default=0)
    requests_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class LogItems(models.Model):
    key_name = models.CharField(max_length=255, default='name')
    file_name = models.CharField(max_length=255)
    blob_url = models.URLField()
    line_number = models.IntegerField(default=0)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class RawItems(models.Model):
    key_name = models.CharField(max_length=255, default='name')
    file_name = models.CharField(max_length=255)
    blob_url = models.URLField()
    line_number = models.IntegerField(default=0)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class LogEntry(models.Model):
    unique_key = models.CharField(max_length=100, db_index=True)
    ip_address = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    method = models.CharField(max_length=10)
    endpoint = models.CharField(max_length=200)
    status_code = models.IntegerField()
    response_size = models.IntegerField()


class LogSummary(models.Model):
    unique_key = models.CharField(max_length=100, db_index=True)
    total_requests = models.IntegerField()
    success_count = models.IntegerField()
    client_error_count = models.IntegerField()
    server_error_count = models.IntegerField()
    top_endpoint = models.CharField(max_length=200)
    top_ip = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)    
