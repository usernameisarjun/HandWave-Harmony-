import cv2
import mediapipe as mp
import numpy as np
import pygame
import time
import threading
import os
import shutil
import soundfile as sf


pygame.init()


DrumBeatt = {
    'kick': 'kick.wav',
    'stick': 'stick.wav',
    'hihat': 'hihat.wav',
    'crash': 'crash.wav'
}


def PlayDrum(script_path, beat):

    pygame.mixer.Sound(os.path.join(os.path.dirname(script_path), DrumBeatt[beat])).play()


def Record(key):
    if recording:
        RecordSeq.append((key, time.time()))


def Save(script_path):
    if RecordSeq:
        AUdiofolder = os.path.join(os.path.dirname(script_path), "audio")
        if not os.path.exists(AUdiofolder):
            os.makedirs(AUdiofolder)
        AudioFile = []
        for i, (key, timestamp) in enumerate(RecordSeq):
            sound_file = os.path.join(os.path.dirname(script_path), DrumBeatt[key])
            if os.path.exists(sound_file):
                AudioFile.append(sound_file)
            else:
                print(f"Error: Sound file '{sound_file}' not found.")
        if AudioFile:
            Output = os.path.join(AUdiofolder, "RecordSeq.wav")
            data, samplerate = sf.read(AudioFile[0])
            for file in AudioFile[1:]:
                d, sr = sf.read(file)
                data = np.concatenate((data, d))
            sf.write(Output, data, samplerate)
            print(f"Recorded sequence saved as {Output}")
        else:
            print("No audio files found for the recorded sequence.")
    else:
        print("No recorded sequence to save.")


def load1():
    return np.load('RecordSeq.npy', allow_pickle=True)


def play1(script_path):
    global Stop
    total_duration = RecordSeq[-1][1] - RecordSeq[0][1]  
    while not Stop:
        start_time = time.time()
        for i in range(len(RecordSeq)):
            key, timestamp = RecordSeq[i]
            next_key, next_timestamp = RecordSeq[(i + 1) % len(RecordSeq)]
            PlayDrum(script_path, key)

            sleep_duration = (next_timestamp - timestamp) / total_duration
            time.sleep(sleep_duration)
        start_time = time.time()


mpDraw = mp.solutions.drawing_utils
mpHand = mp.solutions.hands


pygame.mixer.init()

# Set up the camera
cap = cv2.VideoCapture(0)

##ColoRRRRRR
#white
WHITE = (255, 255, 255)
##
BLACK = (0, 0, 0)
##
GRAY = (128, 128, 128)


keyPress = {beat: None for beat in DrumBeatt.keys()}

# Delay threshold in seconds
DelayKey = 0.1


recording = False


RecordSeq = []


Stop = False

with mpHand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame1 = cap.read()
        if not ret:
            break

        
        frame1 = cv2.flip(frame1, 1)

       ########################################
        rgbFRame = cv2.cvtColor(frame1,   cv2.COLOR_BGR2RGB)

      ##########################################
        results = hands.process(rgbFRame)

        # Draw keys 
        h, w, c = frame1.shape
        ############
        pad_width = int(w / 4)
        pad_height = int(h / 4)
        ############
        for i, (key, _) in enumerate(DrumBeatt.items()):
            pad_x = i * pad_width
            pad_y = int(h * 0.75)
            cv2.rectangle(frame1, (pad_x, pad_y), (pad_x + pad_width, pad_y + pad_height), BLACK, -1)
            cv2.putText(frame1, key, (pad_x + 10, pad_y + pad_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 2)

       
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_finger_tip = hand_landmarks.landmark[mpHand.HandLandmark.INDEX_FINGER_TIP]
                cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

                
                cv2.circle(frame1, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

               
                for key, _ in DrumBeatt.items():
                    pad_x = list(DrumBeatt.keys()).index(key) * pad_width
                    pad_y = int(h * 0.75)
                    if pad_x <= cx <= pad_x + pad_width and pad_y <= cy <= pad_y + pad_height:
                        
                        if keyPress[key] is None or time.time() - keyPress[key] > DelayKey:
                            PlayDrum(os.path.abspath(__file__), key)
                            Record(key)
                            
                            keyPress[key] = time.time()

        cv2.imshow('Air Drum', frame1)

        # Keyboard
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('a'):
            recording = True
            RecordSeq = []
            print("Recording started...")
        elif key == ord('s'):
            recording = False
            Save(os.path.abspath(__file__))
            print("Recording stopped and saved.")
        elif key == ord('d'):
            RecordSeq = load1()
            if len(RecordSeq) > 0:
                print("Playing recorded sequence...")
                Stop = False
                threading.Thread(target=play1, args=(os.path.abspath(__file__),)).start()
            else:
                print("No recorded sequence found.")
        elif key == ord('f'):
            Stop = True
            pygame.mixer.stop()

cap.release()
cv2.destroyAllWindows()
