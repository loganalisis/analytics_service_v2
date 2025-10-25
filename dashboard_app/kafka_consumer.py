from kafka import KafkaConsumer
import json
from .models import LogAnalytics
from django.utils import timezone

print("Received log data:")
consumer = KafkaConsumer(
    'logs.uploaded',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    data = message.value
    print(f"Received log data: {data}")
    # Placeholder logic: you can parse Azure Blob logs and compute metrics
    LogAnalytics.objects.create(
        file_name=data['file'],
        blob_url=data['url'],
        error_count=0,
        requests_count=0,
        created_at=timezone.now()
    )
