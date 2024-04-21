import cv2
import mediapipe as mp
import numpy as np
import pygame
import time
import threading
import tkinter as tk
from tkinter import filedialog

# Initialize Pygame
pygame.init()

# Set up sound
notes = {'C': 261.63, 'D': 293.66, 'E': 329.63, 'F': 349.23, 'G': 392.00, 'A': 440.00, 'B': 493.88}

# Function to play a note
def PlaySounds(note):
    # Load and play the sound corresponding to the note
    pygame.mixer.Sound(f'C:/Users/arjun/OneDrive/Desktop/DTI Handwave harmony/yoo/{note}.wav').play()

# Function to play audio file in loop
def PlayAudio(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play(-1)

# Function to record key presses
def RecordKey(key):
    if recording:
        RecordSeq.append((key, time.time()))

# Function to save recorded sequence
def SaveRecorded():
    np.save('RecordSeq.npy', RecordSeq)

# Function to load recorded sequence
def LoadRecord1():
    return np.load('RecordSeq.npy', allow_pickle=True)

# Function to play recorded sequence in a separate thread
def PlayRecorded1():
    global Stopplay
    while not Stopplay:
        start_time = time.time()
        for i in range(len(RecordSeq)):
            key, timestamp = RecordSeq[i]
            next_key, next_timestamp = RecordSeq[(i + 1) % len(RecordSeq)]
            PlaySounds(key)
            time.sleep(max(0, float(next_timestamp) - float(timestamp)))
            start_time = time.time()

# Function to choose audio file
def choosEAudio():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title="Select Audio File", filetypes=[("WAV files", "*.wav")])
    return file_path

# Initialize mediapipe
mpDraw = mp.solutions.drawing_utils
mpHands = mp.solutions.hands

# Initialize Pygame mixer
pygame.mixer.init()

# Set up the camera
cap = cv2.VideoCapture(0)

# Define colors
WHITE =   (255, 255, 255)
#############3
BLACK  =    (0, 0, 0)
##############
GRAY  =    (128, 128, 128)

# Dictionary to keep track of key press time
keyTime = {key: None for key in notes.keys()}

# Delay threshold in seconds
DelayKey = 0.5

# Flag to indicate recording state
recording = False

# Recorded sequence
RecordSeq = []

# Flag to indicate playback state
Stopplay = False
AdioFileChoose = False

with mpHands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        results = hands.process(rgb_frame)

        # Draw black keys
        h, w, c = frame.shape
        key_width = int(w/7)
        key_height = int(h/4)
        for i, (key, note) in enumerate(notes.items()):
            if key in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
                key_x = i * key_width
                key_y = int(h*0.75)
                cv2.rectangle(frame, (key_x, key_y), (key_x + key_width, key_y + key_height), BLACK, -1)
                cv2.putText(frame, key, (key_x + 10, key_y + key_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 2)

        # Extract index finger tip landmark if available
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_finger_tip = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
                cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

                # Draw circle at the index finger tip
                cv2.circle(frame, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

                # Map index finger tip to piano keys and play sound if within key area
                for key, note in notes.items():
                    if key in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
                        key_x = list(notes.keys()).index(key) * key_width
                        key_y = int(h*0.75)
                        if key_x <= cx <= key_x + key_width and key_y <= cy <= key_y + key_height:
                            # Check if key was not pressed previously or if key press time has exceeded threshold
                            if keyTime[key] is None or time.time() - keyTime[key] > DelayKey:
                                PlaySounds(key)
                                RecordKey(key)
                                # Update key press time
                                keyTime[key] = time.time()

        cv2.imshow('Air Piano', frame)

        # Keyboard input handling
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('r'):
            recording = True
            RecordSeq = []
            print("Recording started...")
        elif key == ord('t'):
            recording = False
            SaveRecorded()
            print("Recording stopped and saved.")
        elif key == ord('l'):
            audio_file = choosEAudio()
            if audio_file:
                PlayAudio(audio_file)
                AdioFileChoose = True
            else:
                AdioFileChoose = False
        elif key == ord('n'):
            Stopplay = True
            pygame.mixer.stop()

cap.release()
cv2.destroyAllWindows()
