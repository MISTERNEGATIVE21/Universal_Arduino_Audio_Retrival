import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
import wave
import pyaudio
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageDraw

class AudioRecorderApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("800x600")  # Set larger window size
        self.root.title("Audio Recorder")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.is_recording = False
        self.my_port = None
        self.audio = pyaudio.PyAudio()
        self.audio_stream = None
        self.playback_stream = None
        self.wave_file = None
        self.audio_data = np.zeros(44100)  # Initialize with zeros to avoid errors

        self.setup_ui()
        self.root.mainloop()

    def setup_ui(self):
        self.setup_serial_ports()
        self.setup_record_button()
        self.setup_canvas()

    def setup_serial_ports(self):
        ports = list(serial.tools.list_ports.comports())
        self.port_names = [port.device for port in ports]

        self.port_label = tk.Label(self.root, text="Select Serial Port:")
        self.port_label.pack()

        self.port_combobox = ttk.Combobox(self.root, values=self.port_names)
        self.port_combobox.pack()
        self.port_combobox.current(0)

    def setup_record_button(self):
        self.record_button = tk.Button(self.root, text="Record", command=self.toggle_recording)
        self.record_button.pack()

    def setup_canvas(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))  # Larger figure size
        self.line, = self.ax.plot([], [])
        self.ax.set_title("Sound Oscilloscope")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_xlim(0, 44100)  # Set initial x-axis limit
        self.ax.set_ylim(-32768, 32768)  # Set initial y-axis limit
        self.fig_canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.fig_canvas.get_tk_widget().pack()

    def toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.record_button.config(text="Stop Recording")
            selected_port = self.port_combobox.get()
            self.my_port = serial.Serial(selected_port, 115200)
            self.start_recording()
            self.play_audio()
        else:
            self.record_button.config(text="Record")
            self.stop_recording()
            self.stop_audio()
            self.my_port.close()
            # Reset the graph to default state
            self.line.set_xdata([])
            self.line.set_ydata([])
            self.ax.set_xlim(0, 44100)
            self.ax.set_ylim(-32768, 32768)
            self.fig_canvas.draw()

    def start_recording(self):
        self.wave_file = wave.open("recorded_audio.wav", 'wb')
        self.wave_file.setnchannels(1)  # Mono
        self.wave_file.setsampwidth(2)   # 2 bytes (16-bit)
        self.wave_file.setframerate(44100)  # Sample rate
        self.audio_stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        stream_thread = threading.Thread(target=self.record_audio)
        stream_thread.start()

    def stop_recording(self):
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None
        if self.wave_file:
            self.wave_file.close()
            self.wave_file = None

    def record_audio(self):
        frames = []
        while self.is_recording:
            data = self.audio_stream.read(1024)
            self.wave_file.writeframes(data)
            new_audio_data = np.frombuffer(data, dtype=np.int16)
            self.audio_data = np.roll(self.audio_data, -len(new_audio_data))
            self.audio_data[-len(new_audio_data):] = new_audio_data
            self.line.set_xdata(np.arange(len(self.audio_data)))
            self.line.set_ydata(self.audio_data)
            self.ax.set_ylim(np.min(self.audio_data), np.max(self.audio_data))
            self.fig_canvas.draw()
            # Capture the figure and append to frames
            self.fig_canvas.draw()
            image = Image.frombytes('RGB', self.fig_canvas.get_width_height(), self.fig_canvas.tostring_rgb())
            frames.append(image)

        # Save frames as GIF
        frames[0].save('sound_oscilloscope.gif', save_all=True, append_images=frames[1:], duration=100, loop=0)

    def play_audio(self):
        self.playback_stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)
        play_thread = threading.Thread(target=self.play_audio_thread)
        play_thread.start()

    def play_audio_thread(self):
        while self.is_recording:
            if self.my_port:
                data = self.my_port.read(1024)
                self.playback_stream.write(data)

    def stop_audio(self):
        if self.playback_stream:
            self.playback_stream.stop_stream()
            self.playback_stream.close()
            self.playback_stream = None

    def on_closing(self):
        if self.is_recording:
            self.toggle_recording()
        self.audio.terminate()
        self.root.destroy()

if __name__ == "__main__":
    AudioRecorderApp()

