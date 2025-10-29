import json

from modules.receiver.domain.ports.queue import QueueRepositoryAbstract


class SQSQueueRepository(QueueRepositoryAbstract):
    def __init__(self, sqs_client, queue_url: str):
        self.sqs_client = sqs_client
        self.queue_url = queue_url

    async def publish(self, message: dict) -> None:
        self.sqs_client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message)
        )