import cv2

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("Could not open camera")
    exit()

print("Camera opened successfully!")

while True:
    success, frame = camera.read()

    print("Frame received:", success)

    if not success:
        print("Could not read frame")
        break

    cv2.imshow("My Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()