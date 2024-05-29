import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, messagebox
import wave
import pyaudio
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from PIL import Image

def toggle_recording():
    global is_recording, frames
    is_recording = not is_recording
    if is_recording:
        my_port.write(b'R')  # Send start recording command
        tk_canvas.itemconfig(circle, fill="red")
        start_recording()
        play_audio()  # Start playing audio simultaneously
        record_button.config(text="Stop Recording")
        frames = []  # Initialize the frames list
    else:
        my_port.write(b'S')  # Send stop recording command
        tk_canvas.itemconfig(circle, fill="green")
        stop_recording()
        stop_audio()  # Stop playing audio
        record_button.config(text="Start Recording")

def start_recording():
    global audio_stream, wave_file
    wave_file = wave.open("recorded_audio.wav", 'wb')
    wave_file.setnchannels(1)  # Mono
    wave_file.setsampwidth(2)   # 2 bytes (16-bit)
    wave_file.setframerate(44100)  # Sample rate
    audio_stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    stream_thread = threading.Thread(target=record_audio)
    stream_thread.start()

def stop_recording():
    global audio_stream, wave_file
    if audio_stream:
        audio_stream.stop_stream()
        audio_stream.close()
        audio_stream = None
    if wave_file:
        wave_file.close()
        wave_file = None
    save_gif()  # Save the recorded frames as a GIF

def record_audio():
    while is_recording:
        data = audio_stream.read(1024)  # Read audio data from PyAudio stream
        wave_file.writeframes(data)
        update_spectrum(data)

def play_audio():
    global playback_stream
    playback_stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)
    play_thread = threading.Thread(target=play_audio_thread)
    play_thread.start()

def play_audio_thread():
    while is_recording:
        data = my_port.read(1024)  # Read audio data from serial port
        playback_stream.write(data)

def stop_audio():
    global playback_stream
    if playback_stream:
        playback_stream.stop_stream()
        playback_stream.close()
        playback_stream = None

def on_closing():
    global is_recording
    if is_recording:
        my_port.write(b'S')  # Send stop recording command
        is_recording = False
        stop_recording()
        stop_audio()
    my_port.close()
    audio.terminate()
    root.destroy()

def create_dummy_wav():
    with wave.open("recorded_audio.wav", 'wb') as dummy_wave:
        dummy_wave.setnchannels(1)  # Mono
        dummy_wave.setsampwidth(2)   # 2 bytes (16-bit)
        dummy_wave.setframerate(44100)  # Sample rate
        dummy_wave.writeframes(b'\x00\x00' * 44100)  # 1 second of silence

def select_port(event):
    global my_port
    selected_port = port_combobox.get()
    if my_port.is_open:
        my_port.close()
    my_port = serial.Serial(selected_port, 115200)

def update_spectrum(data):
    global spectrum_line, frames
    audio_data = np.frombuffer(data, dtype=np.int16)
    fft_result = np.fft.rfft(audio_data)
    freqs = np.fft.rfftfreq(len(audio_data), 1 / 44100)
    spectrum_line.set_ydata(np.abs(fft_result))
    spectrum_line.set_xdata(freqs)
    ax.set_xlim(0, freqs[-1])
    ax.set_ylim(0, np.max(np.abs(fft_result)))

    # Add timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ax.text(0.95, 0.01, timestamp, verticalalignment='bottom', horizontalalignment='right', transform=ax.transAxes, color='white', fontsize=8, bbox={'facecolor': 'black', 'alpha': 0.5, 'pad': 5})
    
    # Draw and save the current frame
    fig_canvas.draw()
    frame = np.frombuffer(fig_canvas.tostring_rgb(), dtype=np.uint8).reshape(fig_canvas.get_width_height()[::-1] + (3,))
    frames.append(frame)

def save_spectrum():
    fig.savefig("spectrum_analysis.png")
    messagebox.showinfo("Save Spectrum", "Spectrum analysis saved as 'spectrum_analysis.png'")

def save_gif():
    global frames
    images = [Image.fromarray(frame) for frame in frames]
    images[0].save('spectrum_analysis.gif', save_all=True, append_images=images[1:], duration=100, loop=0)
    messagebox.showinfo("Save Spectrum", "Spectrum analysis saved as 'spectrum_analysis.gif'")

# Create a dummy .wav file
create_dummy_wav()

# List available ports
ports = list(serial.tools.list_ports.comports())
port_names = [port.device for port in ports]

# Setup PyAudio for recording and playback
audio = pyaudio.PyAudio()

# Setup the UI
root = tk.Tk()
root.title("Audio Recorder")
root.protocol("WM_DELETE_WINDOW", on_closing)

port_label = tk.Label(root, text="Select Serial Port:")
port_label.pack(pady=5)

port_combobox = ttk.Combobox(root, values=port_names)
port_combobox.bind("<<ComboboxSelected>>", select_port)
port_combobox.pack(pady=5)
port_combobox.current(0)

my_port = serial.Serial(port_names[0], 115200)
is_recording = False

# Setup Tkinter Canvas
tk_canvas = tk.Canvas(root, width=200, height=200)
tk_canvas.pack(pady=5)

circle = tk_canvas.create_oval(75, 75, 125, 125, fill="green")

# Buttons for controlling recording and saving spectrum
record_button = tk.Button(root, text="Start Recording", command=toggle_recording)
record_button.pack(pady=5)

save_button = tk.Button(root, text="Save Spectrum", command=save_spectrum)
save_button.pack(pady=5)

# Setup the spectrum analyzer
fig, ax = plt.subplots()
spectrum_line, = ax.plot([], [])
ax.set_title("Spectrum Analyzer")
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Amplitude")
fig_canvas = FigureCanvasTkAgg(fig, master=root)
fig_canvas.get_tk_widget().pack(pady=5)

root.mainloop()
