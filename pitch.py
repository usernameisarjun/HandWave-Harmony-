import cv2
import numpy as np
import pyaudio
import mediapipe as mp

FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 4096  # Increased chunk size for smoother playback

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, output=True,
                    frames_per_buffer=CHUNK)

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

cv2.namedWindow('Camera & Hand Gesture')

def mapPostoPitch(hand_landmarks):
    WristY = hand_landmarks.landmark[mpHands.HandLandmark.WRIST].y
    minPitch = 50
    maxPitch = 500
    pitchRange = maxPitch - minPitch
    posRange = 1.0
    pitch = minPitch + (1 - WristY) * pitchRange / posRange
    return pitch

def ChangePitch1(pitch):
    global PrevPos, pitchMulti

    if PrevPos is None:
        PrevPos = pitch

    PosDiff = pitch - PrevPos
    PrevPos = pitch

    if PosDiff > 0:
        pitchMulti += 0.1
    elif PosDiff < 0:
        pitchMulti -= 0.1

    pitchMulti = max(0.1, min(pitchMulti, 2.0))

    modified_pitch = pitch * pitchMulti
    return modified_pitch

PrevPos = None
pitchMulti = 1.0

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            pitch = mapPostoPitch(hand_landmarks)
            modified_pitch = ChangePitch1(pitch)

            # Generate a constant frequency tone for demonstration
            duration = 0.1
            ToneFreq = modified_pitch
            num_samples = int(duration * RATE)
            t = np.linspace(0, duration, num_samples, endpoint=False)
            tone = np.sin(2 * np.pi * ToneFreq * t)

            # Smooth out the tone using a Blackman window
            tone *= np.blackman(num_samples)

            # Scale the tone to prevent clipping
            tone *= 0.2

            # Play the tone
            stream.write(tone.astype(np.float32).tobytes())

            # Draw hand landmarks and connections
            mpDraw.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS)

    cv2.imshow('Camera & Hand Gesture', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

stream.stop_stream()
stream.close()
audio.terminate()
cv2.destroyAllWindows()
