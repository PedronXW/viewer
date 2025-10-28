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
from modules.receiver.domain.track import TrackProps
from modules.receiver.infra.ports.queues.client import queue_url, sqs
from modules.receiver.infra.ports.queues.SQSQueue import SQSQueueRepository
from modules.receiver.infra.ports.repositories.frame.repository import \
    FrameRepository
from modules.receiver.infra.ports.repositories.track.repository import \
    TrackRepository
from modules.receiver.infra.ports.storage.S3Storage import S3Storage
from modules.receiver.services.frame.create import CreateFrameService
from modules.receiver.services.track.create import CreateTrackService
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
        self.created_at = datetime.utcnow()
        
        print(f"[Consumer] Initialized receiver {self.receiver.id} -> {self.receiver.url}")

    def stop(self):
        self._stop_event.set()
    
    def run(self):
        print(f"[Consumer] Running receiver {self.receiver.id} thread")
        with self.app.app_context():
            asyncio.run(self._run_async())

    async def _run_async(self):
        print(f"[Consumer] Starting receiver {self.receiver.id} -> {self.receiver.url}")
        detector = Detector(config.YOLO_MODEL_PATH)
        cap = get_video_stream(self.receiver.url)

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
            
            results = detector.detect(frame)
            detections, scores = [], []

            
            for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
                if int(cls) in [2, 3, 5, 7]:  # car, motorbike, bus, truck
                    detections.append(box.cpu().numpy())
                    scores.append(conf.item())

            if len(detections) > 0:
                dets = np.concatenate([np.array(detections), np.array(scores).reshape(-1, 1)], axis=1)
            else:
                dets = np.zeros((0, 5), dtype=np.float32)

            img_info = (frame.shape[0], frame.shape[1])
            tracks = tracker.update(dets, img_info, img_info)
            
            for track in tracks:
                x1, y1, x2, y2 = map(int, track.tlbr)
                unique_id = f"{int(self.created_at.timestamp() * 1000)}_{track.start_frame}_{track.track_id}"
                track_repository = TrackRepository()
                track = await track_repository.get(track_id=unique_id)
                if not track:
                    create_track_service = CreateTrackService(track_repository=track_repository)
                    track = create_track_service.execute(props=TrackProps(
                            track_id=unique_id
                    ))
                
                h, w = frame.shape[:2]
                x1 = max(0, min(x1, w - 1))
                x2 = max(0, min(x2, w - 1))
                y1 = max(0, min(y1, h - 1))
                y2 = max(0, min(y2, h - 1))

                if x2 > x1 and y2 > y1:
                    cropped = frame[y1:y2, x1:x2]
            
                    frame_repository = FrameRepository()
                    storage_repository = S3Storage()
                    create_frame_service = CreateFrameService(frame_repository=frame_repository, storage_repository=storage_repository)
                    queue_repository = SQSQueueRepository(sqs_client=sqs, queue_url=queue_url)
                    
                    domain_frame = await create_frame_service.execute(props=FrameProps(
                        id=None,
                        track_id=str(track.id),
                        receiver_id=str(self.receiver.id),
                        timestamp=datetime.utcnow()
                    ), frame_data=cropped)
                    
                    await queue_repository.publish({
                        "receiver_id": str(self.receiver.id),
                        "timestamp": str(datetime.utcnow().isoformat()),
                        "frame_id": domain_frame.id
                    })
            
            
            now = time.time()
            if now - last_hb >= 10:
                with self.app.app_context():
                    self.repository.update_heartbeat(self.receiver.id)
                last_hb = now

        cap.release()
        with self.app.app_context():
            self.repository.release(self.receiver.id)
        print(f"[Consumer] Stopped receiver {self.receiver.id}")