import cv2
import pickle  # To convert face data to text data
import numpy as np  # For numpy array manipulation
import os  # For reading/writing files
import tkinter as tk
from tkinter import messagebox

# Check if 'data' folder exists, if not, create it
if not os.path.exists('data'):
    os.makedirs('data')

# Open video capture
video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')  # Haarcascade is a pre-trained model for face detection

faces_data = []  # Empty data array to store faces

i = 0
name = "Voter"  # Default name for the captured faces
framesTotal = 50  # Total number of frames to capture
captureAfterFrame = 2  # Capture face after every 2 frames

while True:
    ret, frame = video.read()  # Read a frame from the video capture
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert the frame to grayscale
    faces = facedetect.detectMultiScale(gray, 1.3, 5)  # Detect faces in the frame

    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w]  # Crop the face from the frame
        resized_img = cv2.resize(crop_img, (50, 50))  # Resize the cropped face to 50x50

        # Append the resized face image to the faces_data array if conditions are met
        if len(faces_data) <= framesTotal and i % captureAfterFrame == 0:
            faces_data.append(resized_img)
        i += 1

        # Display the number of captured faces on the video feed
        cv2.putText(frame, str(len(faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)

    # Show the video frame
    cv2.imshow('frame', frame)

    # Break the loop if 'a' is pressed or if the required number of faces is captured
    k = cv2.waitKey(1)
    if k == ord('a') or len(faces_data) >= framesTotal:
        break

# Release the video capture and close all OpenCV windows
video.release()
cv2.destroyAllWindows()

# Convert faces_data to a numpy array and reshape it
faces_data = np.asarray(faces_data)
faces_data = faces_data.reshape((framesTotal, -1))

# If names.pkl does not exist, create a new file with the names of the faces
if 'names.pkl' not in os.listdir('data/'):
    names = [name] * framesTotal
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(names, f)
else:
    with open('data/names.pkl', 'rb') as f:
        names = pickle.load(f)
    names = names + [name] * framesTotal
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(names, f)

# If faces_data.pkl does not exist, create a new file with the face data
if 'faces_data.pkl' not in os.listdir('data/'):
    with open('data/faces_data.pkl', 'wb') as f:
        pickle.dump(faces_data, f)
else:
    with open('data/faces_data.pkl', 'rb') as f:
        faces = pickle.load(f)
    faces = np.append(faces, faces_data, axis=0)
    with open('data/faces_data.pkl', 'wb') as f:
        pickle.dump(faces, f)

# Display a success message using tkinter
root = tk.Tk()
root.withdraw()  # Hide the main tkinter window
messagebox.showinfo("Success", "Faces added successfully!")
