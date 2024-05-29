import serial
from serial.tools import list_ports
import wave
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import ttk
from threading import Thread

SERIAL_PORT = 'COM3'  # Change this to your serial port
BAUD_RATE = 115200
WAV_FILENAME = 'recorded_audio.wav'
SAMPLE_RATE = 40000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 2 bytes for 16-bit audio
BUFFER_SIZE = 512

recording = False
selected_port = None
ser = None
audio_data = []

# Function to list available serial ports
def list_serial_ports():
    return [port.device for port in list_ports.comports()]

# Function to read from serial and write to WAV file
def record_audio():
    global recording, ser, audio_data
    audio_data = []
    with wave.open(WAV_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        while recording:
            data = ser.read(BUFFER_SIZE)
            if data:
                audio_data.extend(np.frombuffer(data, dtype=np.int16))
                wf.writeframes(data)

# Function to handle the record button click
def start_recording():
    global recording, ser
    selected_port = port_var.get()
    if selected_port:
        ser = serial.Serial(selected_port, BAUD_RATE)
        recording = True
        record_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        port_menu.config(state=tk.DISABLED)
        thread = Thread(target=record_audio)
        thread.start()
        # thread_plot = Thread(target=plot_spectrum)
        # thread_plot.start()
        plot_spectrum()

# Function to handle the stop button click
def stop_recording():
    global recording, ser
    recording = False
    ser.close()
    record_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    port_menu.config(state=tk.NORMAL)

# Tkinter GUI setup
root = tk.Tk()
root.title('Audio Recorder with Spectrum Analyzer')

frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ports = list_serial_ports()
port_var = tk.StringVar(value=ports[0] if ports else '')

port_label = ttk.Label(frame, text="Select Serial Port:")
port_label.grid(row=0, column=0, padx=5, pady=5)

port_menu = ttk.OptionMenu(frame, port_var, *ports)
port_menu.grid(row=0, column=1, padx=5, pady=5)

record_button = ttk.Button(frame, text='Record', command=start_recording)
record_button.grid(row=1, column=0, padx=5, pady=5)

stop_button = ttk.Button(frame, text='Stop', command=stop_recording)
stop_button.grid(row=1, column=1, padx=5, pady=5)
stop_button.config(state=tk.DISABLED)

# Plotting setup
fig, ax = plt.subplots()
x_data = np.linspace(0, SAMPLE_RATE // 2, BUFFER_SIZE // 2)
y_data = np.zeros(BUFFER_SIZE // 2)
line, = ax.plot(x_data, y_data)
ax.set_xlim(0, SAMPLE_RATE // 2)
ax.set_ylim(0, 1)
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Magnitude')

# Function to update the plot
def update_plot(frame):
    global audio_data
    if len(audio_data) >= BUFFER_SIZE:
        sample = audio_data[-BUFFER_SIZE:]
        audio_data = audio_data[-BUFFER_SIZE:]  # Keep the latest buffer size
        spectrum = np.abs(np.fft.rfft(sample)) / BUFFER_SIZE
        line.set_ydata(spectrum)
        fig.canvas.draw_idle()  # Update the plot
    return line,

# Function to plot the spectrum analyzer
def plot_spectrum():
    ani = FuncAnimation(fig, update_plot, interval=50, blit=True)
    plt.show()

root.mainloop()
