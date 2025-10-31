import json
import os

import cv2
import faiss
import numpy as np
import torch
import torchreid

from modules.analysis.service.ocr import read_plate
from modules.analysis.service.postprocess import correct_ocr
from modules.receiver.domain.ports.storage import StorageRepositoryAbstract


class RunAnalysisService:
    def __init__(self, storage_repository: StorageRepositoryAbstract):
        self.storage_repository = storage_repository
        self.faiss_path = "vehicle_index.faiss"
        self.ids_path = "vehicle_ids.json"

        # 🔹 Modelo: ResNet50 treinado para ReID veicular (VeRi-776)
        self.model = torchreid.models.build_model(
            name="resnet50",
            num_classes=1000,
            pretrained=False
        )

        # 🔹 Baixe o checkpoint veicular (coloque o .pth na mesma pasta)
        # URL oficial (exemplo): https://github.com/KaiyangZhou/deep-person-reid-model-zoo
        # Exemplo de nome: resnet50_vehid-veri776.pth
        torchreid.utils.load_pretrained_weights(
            self.model, "resnet50_vehid-veri776.pth"
        )

        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        self.mean = np.array([0.485, 0.456, 0.406])
        self.std = np.array([0.229, 0.224, 0.225])

        self.index, self.vehicle_ids = self._load_faiss_index()

    def _load_faiss_index(self):
        if os.path.exists(self.faiss_path) and os.path.exists(self.ids_path):
            index = faiss.read_index(self.faiss_path)
            with open(self.ids_path, "r") as f:
                ids = json.load(f)
            return index, ids
        else:
            # 🔹 ResNet50 → embeddings de 2048 floats
            index = faiss.IndexFlatL2(2048)
            return index, []

    def _save_faiss_index(self):
        faiss.write_index(self.index, self.faiss_path)
        with open(self.ids_path, "w") as f:
            json.dump(self.vehicle_ids, f)

    def _preprocess_image(self, img):
        img = cv2.resize(img, (256, 128))
        img = img[:, :, ::-1] / 255.0  # BGR → RGB e normaliza
        img = (img - self.mean) / self.std
        img = torch.tensor(img.transpose(2, 0, 1), dtype=torch.float32).unsqueeze(0)
        return img.to(self.device)

    def _extract_features(self, img):
        with torch.no_grad():
            features = self.model(self._preprocess_image(img))
            features = features.cpu().numpy().astype("float32")
            # 🔹 Normalização L2 para melhor comparação vetorial
            return features / np.linalg.norm(features)

    async def run(self, data):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                print(f"[RunAnalysisService] JSON decode error: {e}")
                return

        if not data:
            return

        receiver_id = data.get("receiver_id")
        track_id = data.get("track_id")
        frame_id = data.get("frame_id")

        frame_data = await self.storage_repository.get(frame_id)
        file_stream = frame_data["file_stream"]

        np_arr = np.frombuffer(file_stream, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            return

        # 🔹 Etapa 1: OCR da placa
        raw_text = read_plate(img)
        text = correct_ocr(raw_text)

        # 🔹 Etapa 2: Extração do embedding do veículo (2048D)
        embedding = self._extract_features(img)

        # 🔹 Etapa 3: Busca no FAISS
        if len(self.vehicle_ids) > 0:
            distances, indices = self.index.search(embedding, k=1)
            best_distance = float(distances[0][0])
            best_match = self.vehicle_ids[indices[0][0]]

            if best_distance < 0.9:
                return

        # 🔹 Etapa 4: Adiciona novo embedding
        self.index.add(embedding)
        self.vehicle_ids.append({
            "receiver_id": receiver_id,
            "track_id": track_id,
            "frame_id": frame_id,
            "plate": text
        })
        self._save_faiss_index()