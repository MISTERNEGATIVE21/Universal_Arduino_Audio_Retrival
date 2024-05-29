import serial
import wave
import struct

# Serial port configuration
serial_port = '/dev/ttyUSB0'  # Update this with your ESP32 serial port
baud_rate = 115200

# WAV file configuration
output_wav_file = 'output.wav'
sample_width = 2  # 16-bit audio
sample_rate = 44100
channels = 1

# Open serial port
ser = serial.Serial(serial_port, baud_rate)

# Open WAV file for writing
wav_file = wave.open(output_wav_file, 'wb')
wav_file.setnchannels(channels)
wav_file.setsampwidth(sample_width)
wav_file.setframerate(sample_rate)

try:
    while True:
        # Read data from serial port
        raw_data = ser.read(sample_width)
        if len(raw_data) == sample_width:
            # Unpack binary data to integer
            audio_sample = struct.unpack('<h', raw_data)[0]
            # Write audio sample to WAV file
            wav_file.writeframesraw(raw_data)
except KeyboardInterrupt:
    pass

# Close serial port and WAV file
ser.close()
wav_file.close()
