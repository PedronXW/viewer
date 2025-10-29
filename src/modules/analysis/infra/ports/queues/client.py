import os

import boto3
from botocore.exceptions import ClientError

# Usa LocalStack se variável estiver ativa
USE_LOCALSTACK = os.getenv("USE_LOCALSTACK", "true").lower() == "true"

# Endpoint LocalStack
LOCALSTACK_ENDPOINT = "http://localstack:4566"

# Cliente SQS
sqs = boto3.client(
    "sqs",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    endpoint_url=LOCALSTACK_ENDPOINT if USE_LOCALSTACK else None
)

queue_name = "frame-added-queue"

try:
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']
    print(f"Fila '{queue_name}' já existe. URL:", queue_url)
except ClientError as e:
    if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
        response = sqs.create_queue(QueueName=queue_name)
        queue_url = response['QueueUrl']
        print(f"Fila '{queue_name}' criada. URL:", queue_url)
    else:
        raise e