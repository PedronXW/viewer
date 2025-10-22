import os
from collections import Counter, defaultdict

import cv2
import numpy as np
import torch
from yolox.tracker.byte_tracker import BYTETracker

import config
from utils.detector import Detector
from utils.ocr import read_plate
from utils.postprocess import correct_ocr
from utils.preprocess import resize_frame
from utils.stream_handler import get_video_stream, read_frame


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

def process_frames():
    detector = Detector(config.YOLO_MODEL_PATH)
    cap = get_video_stream(config.VIDEO_SOURCE)

    frame_idx = 0
    video_writer = None

    while True:
        frame = read_frame(cap)
        if frame is None:
            break

        results = detector.detect(frame)
        detections, scores = [], []

        # filtra apenas veículos
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

        annotated = frame.copy()

        # cria o writer de vídeo apenas uma vez (com base nas dimensões do primeiro frame)
        if video_writer is None:
            h, w = annotated.shape[:2]
            out_path = os.path.join(OUTPUT_DIR, "tracked_video.mp4")
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            video_writer = cv2.VideoWriter(out_path, fourcc, 30, (w, h))

        for track in tracks:
            x1, y1, x2, y2 = map(int, track.tlbr)
            track_id = track.track_id

            # cor fixa por ID
            color = (int(track_id * 37) % 255, int(track_id * 17) % 255, int(track_id * 29) % 255)

            # desenha o retângulo e ID
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                annotated,
                f"ID {track_id}",
                (x1 + 5, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

            # salva o frame do veículo
            vehicle_dir = os.path.join(OUTPUT_DIR, f"vehicle_{track_id}")
            os.makedirs(vehicle_dir, exist_ok=True)

            h, w = frame.shape[:2]
            x1 = max(0, min(x1, w - 1))
            x2 = max(0, min(x2, w - 1))
            y1 = max(0, min(y1, h - 1))
            y2 = max(0, min(y2, h - 1))

            if x2 > x1 and y2 > y1:
                cropped = frame[y1:y2, x1:x2] # recorta o veículo
                raw_text = read_plate(cropped)
                text = correct_ocr(raw_text)

                # atualiza contador de placas
                if text:
                    vehicle_ocr_counter[track_id][text] += 1

                # consulta a placa mais frequente até o momento
                if vehicle_ocr_counter[track_id]:
                    most_common_plate = vehicle_ocr_counter[track_id].most_common(1)[0][0]
                    print(f"Track {track_id}: placa mais confiável até agora: {most_common_plate}")
                cv2.imwrite(os.path.join(vehicle_dir, f"frame_{frame_idx:05d}.jpg"), cropped) # salva a imagem do veículo
            else:
                print(f"[WARN] Frame {frame_idx}: bounding box inválido ({x1},{y1},{x2},{y2}) — ignorado.")

        # adiciona o frame anotado ao vídeo
        video_writer.write(annotated)

        print(f"Frame {frame_idx}: {len(tracks)} veículos rastreados.")
        frame_idx += 1

    cap.release()
    if video_writer is not None:
        video_writer.release()

    print(f"✅ Processamento concluído. Vídeo salvo em: {os.path.join(OUTPUT_DIR, 'tracked_video.mp4')}")
    for vehicle_count in vehicle_ocr_counter.items():
        track_id, plate_counter = vehicle_count
        if plate_counter:
            most_common_plate, count = plate_counter.most_common(1)[0]
            print(f"Veículo ID {track_id}: placa mais confiável final: {most_common_plate} (visto {count} vezes)")
        else:
            print(f"Veículo ID {track_id}: nenhuma placa reconhecida.")