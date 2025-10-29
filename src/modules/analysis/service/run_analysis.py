import json

import cv2
import numpy as np

from modules.analysis.service.ocr import read_plate
from modules.analysis.service.postprocess import correct_ocr
from modules.receiver.domain.ports.storage import StorageRepositoryAbstract


class RunAnalysisService:
    def __init__(self, storage_repository: StorageRepositoryAbstract):
        self.storage_repository = storage_repository
        
    async def run(self, data):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                print(f"[RunAnalysisService] JSON decode error: {e}")
                return
        print(f"[RunAnalysisService] Running analysis service {data}")
        if not data:
            print("[RunAnalysisService] No data to process")
            return
        if "receiver_id" not in data or "track_id" not in data or "frame_id" not in data:
            print("[RunAnalysisService] Missing required data fields")
            return
        receiver_id = data.get("receiver_id")
        track_id = data.get("track_id")
        frame_id = data.get("frame_id")
        
        frame_data = await self.storage_repository.get(frame_id)
        file_stream = frame_data["file_stream"]

        # Converter bytes para imagem
        np_arr = np.frombuffer(file_stream, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            print(f"[RunAnalysisService] Failed to decode image for frame {frame_id}")
            return

        raw_text = read_plate(img)
        
        print(f"[RunAnalysisService] Raw OCR text for frame {frame_id}: {raw_text}")

        text = correct_ocr(raw_text)

        if text:
            print(f"Receiver {receiver_id}, Track {track_id}, Frame {frame_id}: Detected plate: {text}")