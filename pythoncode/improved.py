import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
import wave
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Rest of the code...


def toggle_recording():
    global is_recording
    is_recording = not is_recording
    if is_recording:
        my_port.write(b'R')  # Send start recording command
        tk_canvas.itemconfig(circle, fill="red")
        start_recording()
    else:
        my_port.write(b'S')  # Send stop recording command
        tk_canvas.itemconfig(circle, fill="green")
        stop_recording()

def start_recording():
    global wave_file
    wave_file = wave.open("recorded_audio.wav", 'wb')
    wave_file.setnchannels(1)  # Mono
    wave_file.setsampwidth(2)   # 2 bytes (16-bit)
    wave_file.setframerate(44100)  # Sample rate
    stream_thread = threading.Thread(target=record_audio)
    stream_thread.start()

def stop_recording():
    global wave_file
    if wave_file:
        wave_file.close()
        wave_file = None

def record_audio():
    while is_recording:
        data = my_port.read(1024)  # Read audio data from serial port
        wave_file.writeframes(data)
        update_spectrum(data)

def stop_audio():
    pass  # No need to stop audio playback since we're not using PyAudio

def on_closing():
    global is_recording
    if is_recording:
        my_port.write(b'S')  # Send stop recording command
        is_recording = False
        stop_recording()
    my_port.close()
    root.destroy()

def select_port(event):
    global my_port
    selected_port = port_combobox.get()
    if my_port.is_open:
        my_port.close()
    my_port = serial.Serial(selected_port, 115200)

def update_spectrum(data):
    global spectrum_line
    audio_data = np.frombuffer(data, dtype=np.int16)
    fft_result = np.fft.rfft(audio_data)
    freqs = np.fft.rfftfreq(len(audio_data), 1 / 44100)
    spectrum_line.set_ydata(np.abs(fft_result))
    spectrum_line.set_xdata(freqs)
    ax.set_xlim(0, freqs[-1])
    ax.set_ylim(0, np.max(np.abs(fft_result)))
    fig_canvas.draw()

# List available ports
ports = list(serial.tools.list_ports.comports())
port_names = [port.device for port in ports]

# Setup the UI
root = tk.Tk()
root.title("Audio Recorder")
root.protocol("WM_DELETE_WINDOW", on_closing)

port_label = tk.Label(root, text="Select Serial Port:")
port_label.pack()

port_combobox = ttk.Combobox(root, values=port_names)
port_combobox.bind("<<ComboboxSelected>>", select_port)
port_combobox.pack()
port_combobox.current(0)

my_port = serial.Serial(port_names[0], 115200)
is_recording = False

# Setup Tkinter Canvas
tk_canvas = tk.Canvas(root, width=200, height=200)
tk_canvas.pack()

circle = tk_canvas.create_oval(75, 75, 125, 125, fill="green")

tk_canvas.bind("<Button-1>", lambda e: toggle_recording())

# Setup the spectrum analyzer
fig, ax = plt.subplots()
spectrum_line, = ax.plot([], [])
ax.set_title("Spectrum Analyzer")
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Amplitude")
fig_canvas = FigureCanvasTkAgg(fig, master=root)
fig_canvas.get_tk_widget().pack()

root.mainloop()
