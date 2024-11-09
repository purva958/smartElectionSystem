import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from tkinter import *
from tkinter import messagebox  # Import messagebox
from PIL import Image, ImageTk
from sklearn.neighbors import KNeighborsClassifier
from win32com.client import Dispatch

def speak(str1):
    speak = Dispatch("SAPI.Spvoice")
    speak.Speak(str1)

# Tkinter setup
root = Tk()
root.title("Voting System")
root.geometry("800x600")

# OpenCV video feed setup
video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load pre-trained data
if not os.path.exists('data/'):
    os.makedirs('data/')

with open('data/names.pkl', 'rb') as f:
    LABELS = pickle.load(f)

with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

# Create the canvas to display video
video_label = Label(root)
video_label.pack()

# CSV headers
COL_NAMES = ['NAME', 'VOTE', 'DATE', 'TIME']

# Function to check if the user has already voted
def check_if_exists(value):
    try:
        with open("Votes.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row and row[0] == value:
                    return True
    except FileNotFoundError:
        print("File Not Found or Unable to open the CSV file.")
    return False

# Function to record the vote
def record_vote(party_name):
    global output, frame
    ts = time.time()
    date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
    timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
    exist = os.path.isfile("Votes.csv")
    
    voter_exist = check_if_exists(output[0])
    if voter_exist:
        print("YOU HAVE ALREADY VOTED")
        speak("YOU HAVE ALREADY VOTED")
        return
    
    speak(f"YOUR VOTE FOR {party_name} HAS BEEN RECORDED")
    time.sleep(3)
    
    attendance = [output[0], party_name, date, timestamp]
    if exist:
        with open("Votes.csv", "a") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(attendance)
    else:
        with open("Votes.csv", "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(COL_NAMES)
            writer.writerow(attendance)

    # Display success message box
    messagebox.showinfo("Vote Cast", "Your vote has been cast successfully!")  # Message box after vote

    speak("THANK YOU FOR VOTING")

# Button click events for voting
def vote_party1():
    record_vote("PARTY 1")

def vote_party2():
    record_vote("PARTY 2")

def vote_party3():
    record_vote("PARTY 3")

def vote_party4():
    record_vote("PARTY 4")

# Buttons for voting
button1 = Button(root, text="Vote for Party 1", command=vote_party1, width=20)
button1.pack(pady=10)

button2 = Button(root, text="Vote for Party 2", command=vote_party2, width=20)
button2.pack(pady=10)

button3 = Button(root, text="Vote for Party 3", command=vote_party3, width=20)
button3.pack(pady=10)

button4 = Button(root, text="Vote for Party 4", command=vote_party4, width=20)
button4.pack(pady=10)

# Function to update video feed
def update_frame():
    global output, frame
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w]
        resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
        output = knn.predict(resized_img)
        
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
        cv2.rectangle(frame, (x, y-40), (x+w, y), (50, 50, 255), -1)
        cv2.putText(frame, str(output[0]), (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
    
    # Convert frame to ImageTk for displaying in Tkinter
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)
    
    # Call the update_frame function repeatedly
    video_label.after(10, update_frame)

# Start video feed
update_frame()

# Start the Tkinter event loop
root.mainloop()

# Release video and close all windows after exit
video.release()
cv2.destroyAllWindows()
