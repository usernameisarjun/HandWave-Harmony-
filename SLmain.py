import streamlit as st
import subprocess
import psutil

# Global variable to store the running process
current_process = None

def open_code(filename):
    global current_process

    # Terminate the previous process if it exists
    if current_process:
        terminate_process(current_process)

    # Start the new process
    st.sidebar.write(f"Opening {filename}...")
    current_process = subprocess.Popen(["python", filename])

def terminate_process(process):
    try:
        process.terminate()
    except psutil.NoSuchProcess:
        pass

def main():
    # Set layout to appear on the left side of the screen
    st.sidebar.title("Drum and Piano Selector")
    
    if st.sidebar.button("Open Drum"):
        open_code("newdrumm.py")

    if st.sidebar.button("Open Piano"):
        open_code("PianoLoop.py")

    if st.sidebar.button("Pitch Modifier"):
        open_code("pitch.py")

if __name__ == "__main__":
    main()
