import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort

import config
from utils.detector import Detector
from utils.ocr import read_plate
from utils.postprocess import correct_ocr
from utils.preprocess import resize_frame
from utils.stream_handler import get_video_stream, read_frame

tracker = DeepSort(max_age=30, n_init=3)

def process_frames():
    detector = Detector(config.YOLO_MODEL_PATH)
    cap = get_video_stream(config.VIDEO_SOURCE)

    while True:
        frame = read_frame(cap)
        if frame is None:
            break

        frame_resized = resize_frame(frame)
        detections = detector.detect(frame_resized)

        if config.USE_TRACKING and len(detections) > 0:
            formatted_detections = []
            for det in detections:
                x1, y1, x2, y2 = map(int, det['box'])
                conf = det.get('conf', 1.0)
                cls = det.get('cls', 0)
                formatted_detections.append([[x1, y1, x2, y2], conf, cls, None])

            print("Updating tracker with detections...")

            tracks = tracker.update_tracks(formatted_detections, frame=frame_resized)
            for trk in tracks:

                x, y, w, h = map(int, trk.to_ltwh())

                # 🔹 1. Pequena margem no recorte para compensar bounding box
                margin = 5
                x1 = max(x - margin, 0)
                y1 = max(y - margin, 0)
                x2 = min(x + w + margin, frame_resized.shape[1])
                y2 = min(y + h + margin, frame_resized.shape[0])
                plate_img = frame_resized[y1:y2, x1:x2]

                # 🔹 2. OCR e correção do texto (agora mais restrita)
                raw_text = read_plate(plate_img)
                
                print(f"Track {trk.track_id}: OCR bruto ({raw_text})")
                text = correct_ocr(raw_text)

                # 🔹 3. Validar se realmente parece uma placa
                if not text or len(text) < 7:
                    print(f"Track {trk.track_id}: OCR ignorado ({raw_text})")
                    continue

                cv2.imwrite(f"frame_{trk.track_id}.jpg", plate_img)
                print(f"Track ID: {trk.track_id}, Plate: {text}")

        print("Processing complete.")

    cap.release()