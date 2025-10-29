import asyncio
import time

from modules.analysis.infra.ports.storage.S3Storage import S3Storage
from modules.receiver.infra.ports.queues.client import queue_url, sqs
from src.modules.analysis.service.run_analysis import RunAnalysisService


class NewFrameQueueReceiver:
    def receive(self) -> None:
        while True:
            messages = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=10
            )

            if "Messages" in messages:
                storage_repository = S3Storage()
                run_analysis_service = RunAnalysisService(storage_repository=storage_repository)

                for msg in messages["Messages"]:
                    asyncio.run(run_analysis_service.run(msg["Body"]))

                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=msg["ReceiptHandle"]
                    )
            else:
                time.sleep(1)