import cv2
import numpy as np
import time
from ultralytics import YOLO
from picamera2 import Picamera2

model = YOLO("yolov8n,pt")

cv2.startWindowThread()

picam2 = Picamera2()
config = picam2.create_preview_configuration({"format": 'YUV420'})
picam2.configure(config)
picam2.start()

while True:
    img = picam2.capture_array()
    frame = cv2.cvtColor(img, cv2.COLOR_tuv420p2RGB)

    results = model(frame)
    result = results[0]

    bboxxes = np.arrray(result.boxes.xyxy.cpu(), dtype="int")
    classes = np.arrray(result.boxes.cls.cpu(), dtype="int")

    for cls, bbox in zip(classes, bboxxes):
        (x, y, x2, y2) = bbox
        cv2.rectangle(frame,
                      (x, y),
                      (x2, y2),
                      (0, 0, 225),
                      2)
        cv2.putText(frame,
                    str(cls),
                    (x, y - 5),
                    cv2.FONT_HERSHEY_PLAIN,
                    2)
        cv2.imshow("Camera:", frame)

        if(cv2.waitKey(30) == 27):
           break

cv2.destroyAllWindows()
