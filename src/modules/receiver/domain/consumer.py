import asyncio
import os
import threading
import time
from collections import Counter, defaultdict
from datetime import datetime

import cv2
import numpy as np
from yolox.tracker.byte_tracker import BYTETracker

import config as config
from modules.receiver.domain.frame import FrameProps
from modules.receiver.infra.ports.queues.client import queue_url, sqs
from modules.receiver.infra.ports.queues.SQSQueue import SQSQueueRepository
from modules.receiver.infra.ports.repositories.frame.repository import \
    FrameRepository
from modules.receiver.infra.ports.storage.S3Storage import S3Storage
from modules.receiver.services.frame.create import CreateFrameService
from utils.detector import Detector
from utils.ocr import read_plate
from utils.postprocess import correct_ocr
from utils.stream_handler import get_video_stream


class TrackerArgs:
    track_thresh = 0.5
    track_buffer = 30
    match_thresh = 0.8
    frame_rate = 30
    mot20 = False

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
vehicle_ocr_counter = defaultdict(Counter)
np.float = float

tracker = BYTETracker(TrackerArgs())

class ReceiverConsumer(threading.Thread):
    def __init__(self, app, repository, receiver):
        super().__init__(daemon=True)
        self.app = app
        self.repository = repository
        self.receiver = receiver
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()
    
    def run(self):
        with self.app.app_context():
            asyncio.run(self._run_async())

    async def _run_async(self):
        print(f"[Consumer] Starting receiver {self.receiver.id} -> {self.receiver.url}")
        detector = Detector(config.YOLO_MODEL_PATH)
        cap = get_video_stream(self.receiver.url)

        frame_idx = 0
        video_writer = None

        if not cap.isOpened():
            print(f"[Consumer] Failed to open {self.receiver.id}")
            # ensure DB reflects not running
            with self.app.app_context():
                self.repository.release(self.receiver.id)
            return

        # initial heartbeat already set on acquire, but ensure update loop
        last_hb = time.time()
        while not self._stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                # stream lost — wait and let the watcher handle stale locks
                time.sleep(1)
                continue

            frame_repository = FrameRepository()
            storage_repository = S3Storage()
            create_frame_service = CreateFrameService(frame_repository=frame_repository, storage_repository=storage_repository)
            queue_repository = SQSQueueRepository(sqs_client=sqs, queue_url=queue_url)
            

            frame = await create_frame_service.execute(props=FrameProps(
                id=None,
                receiver_id=str(self.receiver.id),
                timestamp=datetime.utcnow()
            ), frame_data=frame)
            
            await queue_repository.publish({
                "receiver_id": str(self.receiver.id),
                "timestamp": str(datetime.utcnow().isoformat()),
                "frame_id": frame.id
            })
            
            
            now = time.time()
            if now - last_hb >= 10:
                with self.app.app_context():
                    self.repository.update_heartbeat(self.receiver.id)
                last_hb = now

        cap.release()
        # on normal stop, release lock
        with self.app.app_context():
            self.repository.release(self.receiver.id)
        print(f"[Consumer] Stopped receiver {self.receiver.id}")