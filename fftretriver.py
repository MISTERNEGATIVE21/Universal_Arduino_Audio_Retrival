import serial
import numpy as np
import matplotlib.pyplot as plt

SERIAL_PORT = 'COM3'  # Change this to your ESP32's serial port (e.g., COM3)
BAUD_RATE = 115200

def main():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

    try:
        while True:
            line = ser.readline().decode().strip()
            if line.startswith('[') and line.endswith(']'):
                # Extract FFT data from the line
                data_str = line[1:-1]
                data_pairs = [pair.split(':') for pair in data_str.split(',')]
                bins = [pair[0].strip()[1:-1] for pair in data_pairs]
                values = [float(pair[1].strip()) for pair in data_pairs]

                # Plot the spectrum
                plt.bar(bins, values)
                plt.xlabel('Frequency Bins')
                plt.ylabel('Magnitude')
                plt.title('Spectrum Analysis')
                plt.show()
    except KeyboardInterrupt:
        ser.close()

if __name__ == '__main__':
    main()
