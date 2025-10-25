from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import LogAnalytics, LogItems, RawItems
from .serializers import LogAnalyticsSerializer
from kafka import KafkaConsumer
import json
from django.utils import timezone
from .parser import process_logs_by_key

from azure.storage.blob import BlobServiceClient
import os

@api_view(['POST'])
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

# @api_view(['GET'])
def get_Log_file(blob_name, url):

    account_name = "subhamstoragelogs"
    # account_key = "lNduVfrpwSM48iJbJNz/PDIxAG39J01lEt/HoWiLxT5/x5cbE6cCw/nZ0WD03NCPHuN/ZCv+ddys+AStNsn0ww=="
    container_name = "loguploadblob"
    blob_name = blob_name

    # Connect to Azure Blob Service
    blob_service_client = BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net",
        credential=account_key
    )

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Download blob contents
    with open("downloaded_log.log", "wb") as f:
        download_stream = blob_client.download_blob()
        f.write(download_stream.readall())

    with open("downloaded_log.log", 'r') as f:
        for line_num, line in enumerate(f):
            if line.strip():
                RawItems.objects.create(
                    key_name=blob_name,
                    file_name=blob_name,
                    blob_url=url,
                    content=line.strip(),
                    line_number=line_num + 1,
                    created_at=timezone.now()
                )


@api_view(['POST'])
def insert_data(request):

    print("Received log data:")
    unique_key = request.data.get("unique_key")
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
            if data['file'] == unique_key:
                get_Log_file(data['file'], data['url'])
            # if data != "hello":
            #     RawItems.objects.create(
            #         key_name=message.key.decode('utf-8'),
            #         file_name=data['file_name'],
            #         blob_url=data['blob_url'],
            #         content=data['content'],
            #         line_number=data['line_number'],
            #         created_at=timezone.now()
            # )
    except KeyboardInterrupt:
                self.stdout.write("Consumer interrupted, closing...")
    finally:
        # Close the consumer when done or on error
        consumer.close()

    return Response({"status": "Data insertion process completed." })
