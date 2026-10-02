from deepface import DeepFace
result = DeepFace.analyze(img_path = "captured_face.jpg", actions=["emotion"])
print(result)