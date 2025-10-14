from ultralytics import YOLO

# Carregar modelo pré-treinado
model = YOLO('models/yolov8s.pt')

# Treinar
model.train(
    data="./dataset.yaml",
    epochs=20,
    batch=4,  # menor para CPU
    device='cpu',
    workers=8,  # menos workers para economizar memória
    mosaic=False, mixup=False, augment=False
)

# Salvar modelo fine-tunado
model.export(format='pt')
