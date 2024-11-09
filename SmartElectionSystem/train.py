import os
import numpy as np
import pickle
from sklearn.neighbors import KNeighborsClassifier

face_data = []
labels = []

for user_dir in os.listdir('data'):
    user_path = os.path.join('data', user_dir)
    if os.path.isdir(user_path):
        with open(f'{user_path}/faces_data.pkl', 'rb') as f:
            faces = pickle.load(f)
            face_data.append(faces)
            labels += [user_dir] * faces.shape[0]  # The label is the Aadhaar number

face_data = np.vstack(face_data)  # Combine all face data

# Train the KNN model
model = KNeighborsClassifier(n_neighbors=3)
model.fit(face_data, labels)


with open('face_recognition_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model trained and saved.")