import cv2

print("OpenCV version:", cv2.__version__)

camera = cv2.VideoCapture(0)

print("Camera opened:", camera.isOpened())

for i in range(10):
    success, frame = camera.read()
    print("Frame", i, "received:", success)

camera.release()