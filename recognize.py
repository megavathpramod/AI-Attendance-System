import face_recognition
import pickle
import numpy as np
import cv2

with open("models/encodings.pkl", "rb") as f:
    data = pickle.load(f)

def recognize_faces(image_path):

    image = cv2.imread(image_path)
    if image is None:
        return []

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    locations = face_recognition.face_locations(rgb, model="hog", number_of_times_to_upsample=2)

    if len(locations) == 0:
        return []

    encodings = face_recognition.face_encodings(rgb, locations)

    results = []

    for (top, right, bottom, left), encoding in zip(locations, encodings):

        distances = face_recognition.face_distance(data["encodings"], encoding)
        best_match_index = np.argmin(distances)

        matches = face_recognition.compare_faces(
            data["encodings"],
            encoding,
            tolerance=0.45
        )

        if matches[best_match_index]:
            name = data["names"][best_match_index]
            enroll = data["enrolls"][best_match_index]
            confidence = (1 - distances[best_match_index]) * 100

            if confidence < 50:
                name = "Unknown"
                enroll = "N/A"
                confidence = 0
        else:
            name = "Unknown"
            enroll = "N/A"
            confidence = 0

        print("Detected:", name, "| Confidence:", round(confidence, 2))

        face_img = image[top:bottom, left:right]

        results.append({
            "name": name,
            "enroll": enroll,
            "confidence": round(confidence, 2),
            "face": face_img
        })

    unique = {}
    for r in results:
        unique[r["enroll"]] = r

    return list(unique.values())
