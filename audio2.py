import cv2
import numpy as np
import pyaudio
import matplotlib.pyplot as plt
import mediapipe as mp

# Audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open default audio input stream
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialize OpenCV window for camera and hand gesture
cv2.namedWindow('Camera & Hand Gesture')

# Initialize variables for audio graph
fig, ax = plt.subplots()
x = np.arange(0, CHUNK)
line, = ax.plot(x, np.zeros(CHUNK))
plt.ion()  # Enable interactive mode

def detect_pitch(audio_data):
    corr = np.correlate(audio_data, audio_data, mode='full')
    corr = corr[len(corr)//2:]

    # Find the peak in the autocorrelation function (excluding the first peak)
    peak_index = np.argmax(corr[1:]) + 1

    # Calculate pitch (in Hz)
    pitch = RATE / peak_index
    return pitch

def display_audio_graph():
    while True:
        # Read audio input from stream
        data = stream.read(CHUNK)
        # Convert audio input to numpy array
        audio_data = np.frombuffer(data, dtype=np.int16)

        # Compute pitch
        pitch = detect_pitch(audio_data)

       
        line.set_ydata(audio_data)
        ax.relim()
        ax.autoscale_view(True, True)

       
        plt.draw()
        plt.pause(0.001)

        
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'): 
            break


cap = cv2.VideoCapture(0)  
while True:
    
    ret, frame = cap.read()

    if not ret:
        break

    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    
    cv2.imshow('Camera & Hand Gesture', frame)

   
    key = cv2.waitKey(1)
    if key & 0xFF == ord('g'):  
        display_audio_graph()
    elif key & 0xFF == ord('q'):  
        break


stream.stop_stream()
stream.close()
audio.terminate()
cv2.destroyAllWindows()
