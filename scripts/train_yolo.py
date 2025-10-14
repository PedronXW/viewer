from ultralytics import YOLO
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--data', type=str, required=True)
parser.add_argument('--epochs', type=int, default=50)
parser.add_argument('--imgsz', type=int, default=640)
args = parser.parse_args()

model = YOLO('yolov8l.pt')
model.train(data=args.data, epochs=args.epochs, imgsz=args.imgsz, augment=True)
