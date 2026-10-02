import cv2
from deepface import DeepFace

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("Could not open camera")
    exit()

print("Camera opened!")
print("Press SPACE to take the picture.")
print("Press Q to cancel.")

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read frame")
        break

    cv2.imshow("Pose For The Gram", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord(" "):
        cv2.imwrite("captured_face.jpg", frame)
        print("Picture saved as captured_face.jpg")
        break

    if key == ord("q"):
        print("Camera cancelled.")
        break

camera.release()
cv2.destroyAllWindows()


# Analyze the captured picture
print("Analyzing your emotion...")

result = DeepFace.analyze(
    img_path="captured_face.jpg",
    actions=["emotion"]
)

print("Emotion result:")
print(result)

print("Dominant emotion:", result[0]["dominant_emotion"])