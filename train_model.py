import os
import face_recognition
import pickle
import pandas as pd
import cv2

DATASET_PATH = "dataset"
CSV_PATH = "names_enroll_branch.csv"
MODEL_PATH = "models/encodings.pkl"

df = pd.read_csv(CSV_PATH)
name_to_enroll = dict(zip(df['name'], df['enroll_no']))

known_encodings = []
known_names = []
known_enrolls = []

print("🚀 Training started...")

for person_name in os.listdir(DATASET_PATH):

    folder = os.path.join(DATASET_PATH, person_name)

    if not os.path.isdir(folder):
        continue

    person_clean = person_name.lower().replace(" ", "_")

    if person_clean not in name_to_enroll:
        print(f"⚠️ Skipping {person_name}")
        continue

    enroll = name_to_enroll[person_clean]

    for img_name in os.listdir(folder):

        path = os.path.join(folder, img_name)

        image = cv2.imread(path)

        if image is None:
            continue

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 🔥 Better detection during training
        locations = face_recognition.face_locations(
            rgb,
            model="cnn",
            number_of_times_to_upsample=2
        )

        if len(locations) == 0:
            print(f"❌ No face in {img_name}")
            continue

        encodings = face_recognition.face_encodings(rgb, locations)

        for encoding in encodings:
            known_encodings.append(encoding)
            known_names.append(person_clean)
            known_enrolls.append(enroll)

        print(f"✅ Processed {img_name}")

# Save model
data = {
    "encodings": known_encodings,
    "names": known_names,
    "enrolls": known_enrolls
}

os.makedirs("models", exist_ok=True)

with open(MODEL_PATH, "wb") as f:
    pickle.dump(data, f)

print("🎉 Training completed!")
print("Total encodings:", len(known_encodings))
