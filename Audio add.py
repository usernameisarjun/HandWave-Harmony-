import cv2
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import tkinter as tk
from tkinter import filedialog
import os
import threading

class AudioRecorderApp:
    def __init__(self, master):
        self.master = master
        self.fs = 44100  # Sample rate
        self.duration = 5  # seconds
        self.audio_data = None
        self.recording = False
        self.save_path = None

        self.frame = tk.Frame(self.master)
        self.frame.pack()

        self.start_button = tk.Button(self.frame, text="Start Recording", command=self.start_recording)
        self.start_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(self.frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.frame, text="Save Recording", command=self.save_recording, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT)

        self.open_button = tk.Button(self.frame, text="Open Saved File", command=self.open_saved_file, state=tk.DISABLED)
        self.open_button.pack(side=tk.LEFT)

        # Create thread for camera
        self.camera_thread = threading.Thread(target=self.start_camera)

    def start_recording(self):
        self.recording = True
        self.audio_data = []
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)
        self.open_button.config(state=tk.DISABLED)
        print("Recording...")

        # Start camera thread
        self.camera_thread.start()

        def callback(indata, frames, time, status):
            if status:
                print(status)
            self.audio_data.append(indata.copy())

        with sd.InputStream(channels=1, samplerate=self.fs, callback=callback):
            sd.sleep(int(self.duration * 1000))

        print("Recording finished.")
        self.stop_recording()

    def stop_recording(self):
        self.recording = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)
        self.open_button.config(state=tk.NORMAL)

    def save_recording(self):
        self.save_path = filedialog.asksaveasfilename(defaultextension=".wav")
        if self.save_path:
            audio_data_concatenated = np.concatenate(self.audio_data)
            write(self.save_path, self.fs, audio_data_concatenated)
            print(f"Audio saved to {self.save_path}")

    def open_saved_file(self):
        if self.save_path:
            os.startfile(self.save_path)

    def start_camera(self):
        # Open camera
        cap = cv2.VideoCapture(0)
        while self.recording:
            ret, frame = cap.read()
            if ret:
                
                cv2.imshow('Camera Feed', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        # Release camera
        cap.release()
        cv2.destroyAllWindows()

def main():
    root = tk.Tk()
    root.title("Audio Recorder")

    app = AudioRecorderApp(root)

    root.mainloop()

if __name__ == "__main__":
    main()
