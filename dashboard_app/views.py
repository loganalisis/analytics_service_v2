from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import LogAnalytics, LogItems
from .serializers import LogAnalyticsSerializer
from kafka import KafkaConsumer
import json
from django.utils import timezone

@api_view(['GET'])
def get_dashboard(request):

    logs = LogItems.objects.all().order_by('-created_at')
    serializer = LogAnalyticsSerializer(logs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def insert_data(request):

    print("Received log data:")
    consumer = KafkaConsumer(
        'logs_item2.uploaded',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',  # Start reading from the earliest message if no committed offset exists
        enable_auto_commit=True, 
    )
    # print("Received log data:", consumer)

    try:
        for message in consumer:
            data = message.value
            # message is a ConsumerRecord object
            print(f"Received message from topic '{message.topic}', partition {message.partition}, offset {message.offset}:")
            print(f"Key: {message.key.decode('utf-8') if message.key else None}, Value: {message.value}")
            if data != "hello":
                LogItems.objects.create(
                    key_name=message.key.decode('utf-8'),
                    file_name=data['file_name'],
                    blob_url=data['blob_url'],
                    content=data['content'],
                    line_number=data['line_number'],
                    created_at=timezone.now()
            )
    except KeyboardInterrupt:
                self.stdout.write("Consumer interrupted, closing...")
    finally:
        # Close the consumer when done or on error
        consumer.close()

    return Response({"status": "Data insertion process completed." })
