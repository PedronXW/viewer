import time

from modules.receiver.infra.ports.queues.client import queue_url, sqs


class NewFrameQueueReceiver:
    def receive(self) -> None:
        print("[Consumer] Starting SQS consumer loop")
        while True:
            messages = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=10
            )
            if "Messages" in messages:
                for msg in messages["Messages"]:
                    print("Mensagem recebida:", msg["Body"])
                    # Processa mensagem...
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=msg["ReceiptHandle"]
                    )
            else:
                time.sleep(1)
