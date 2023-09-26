# import torch
from ultralytics import YOLO

# Model
# model = torch.hub.load('ultralytics/yolov8', 'yolov8m', pretrained=True)
model = YOLO('yolov8n.pt')

def get_tags(img, trust_repo=True):
    res = model(img)
    cls = set()
    for cno in res[0].boxes.cls:
        cls.add(model.names[int(cno)])
    # print(cls)
    return cls
