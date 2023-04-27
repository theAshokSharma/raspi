import numpy as np
import cv2


def gstreamer_pipeline(device,
                       capture_width,
                       capture_height,
                       framerate,
                       display_width,
                       display_height):

    pl = (f"{device} ! video/x-raw, width={capture_width}, height={capture_height}, "
          f"framerate={framerate}/1 ! videoconvert ! videoscale ! video/x-raw,"
          f"width={display_width}, height={display_height} ! appsink")
    return pl


capture_width = 1280
capture_height = 720
display_width = 950
display_height = 600
framerate = 30

pipeline = gstreamer_pipeline("libcamerasrc",
                              capture_width,
                              capture_height,
                              framerate,
                              display_width,
                              display_height)

cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)


while True:
    ret, frame = cap.read()

    if not ret:
        print("failed to read image.")
        break

    if frame is None:
        print("Frame empty, image capture failed.")
        break

    width = int(cap.get(3))
    height = int(cap.get(4))

    font = cv2.FONT_HERSHEY_SIMPLEX
    img = cv2.putText(frame, 'This is Ashok Sharma! ',
                      (10, height - 10),
                      font,
                      1,
                      (0, 0, 0),
                      2,
                      cv2.LINE_AA)

    cv2.imshow('Frame:', img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
