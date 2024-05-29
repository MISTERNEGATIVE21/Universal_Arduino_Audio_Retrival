import socket
import wave
import threading
import tkinter as tk
from tkinter import messagebox
from struct import unpack

# Parameters
HOST = '192.168.1.16'  # IP address of the ESP32
PORT = 80             # Port number used by the ESP32
BUFFER_SIZE = 512     # Buffer size as defined in the Arduino code
SAMPLE_RATE = 40000   # Sample rate as defined in the Arduino code

# Global variables
is_recording = False
audio_data = []

# Function to connect to ESP32 and receive audio data
def receive_audio():
    global is_recording, audio_data

    # Connect to the ESP32 server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while is_recording:
            data = s.recv(BUFFER_SIZE * 2)  # Each sample is 2 bytes (int16_t)
            if not data:
                break
            audio_data.append(data)

    # Save the received audio data as a WAV file
    save_audio()

# Function to save the audio data to a WAV file
def save_audio():
    global audio_data

    # Convert the list of bytes to a single bytes object
    raw_data = b''.join(audio_data)

    # Decode the raw data to PCM format
    decoded_data = unpack('<' + 'h' * (len(raw_data) // 2), raw_data)

    # Convert to bytes for wave writing
    pcm_data = b''.join([wave.struct.pack('<h', sample) for sample in decoded_data])

    with wave.open("recorded_audio.wav", "wb") as wf:
        wf.setnchannels(1)  # Mono audio
        wf.setsampwidth(2)  # 2 bytes per sample (int16_t)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_data)

    messagebox.showinfo("Info", "Recording saved as recorded_audio.wav")

# Function to start recording
def start_recording():
    global is_recording, audio_data

    is_recording = True
    audio_data = []

    thread = threading.Thread(target=receive_audio)
    thread.start()

    record_button.config(bg="red")
    stop_button.config(bg="gray")

# Function to stop recording
def stop_recording():
    global is_recording
    is_recording = False

    record_button.config(bg="gray")
    stop_button.config(bg="green")

# Set up the Tkinter interface
root = tk.Tk()
root.title("Audio Recorder")

record_button = tk.Button(root, text="Start Recording", command=start_recording, bg="gray")
record_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Recording", command=stop_recording, bg="green")
stop_button.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
