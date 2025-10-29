

import io

import cv2

from modules.analysis.domain.ports.storage import StorageRepositoryAbstract
from modules.analysis.infra.ports.storage.client import s3


class S3Storage(StorageRepositoryAbstract):
    async def save(self, frame, frameId) -> None:
        print(f"[S3Storage] Saving frame {frameId} to S3")
        _, buffer = cv2.imencode(".jpg", frame)
        file_stream = io.BytesIO(buffer)
        s3.upload_fileobj(file_stream, "frames", frameId)

    async def get(self, identifier: str) -> dict:
        response = s3.get_object(Bucket="frames", Key=identifier)
        file_stream = response['Body'].read()
        return {"file_stream": file_stream}