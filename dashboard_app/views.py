from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import LogAnalytics, LogItems, RawItems
from .serializers import LogAnalyticsSerializer
from kafka import KafkaConsumer
import json
from django.utils import timezone
from .parser import process_logs_by_key

@api_view(['GET'])
def get_dashboard(request):

    """Trigger log processing by unique key"""
    unique_key = request.data.get("unique_key")
    if not unique_key:
        return Response({"error": "unique_key is required"}, status=400)

    result = process_logs_by_key(unique_key)

    # logs = RawItems.objects.all().order_by('-created_at')
    # serializer = LogAnalyticsSerializer(logs, many=True)

    if "error" in result:
        return Response(result, status=404)
    return Response({
        "message": "Logs processed successfully",
        "summary": result
    })

@api_view(['GET'])
def insert_data(request):

    print("Received log data:")
    consumer = KafkaConsumer(
        'logs_item_updated.uploaded',
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
                RawItems.objects.create(
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
