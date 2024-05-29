#include <Arduino.h>

#define SAMPLE_RATE 40000  // Sample rate in Hz (adjust as needed)
#define BUFFER_SIZE 512   // Buffer size for storing samples
#define ADC_PIN A0        // ADC pin for analog input

unsigned long lastSampleTime = 0;
int16_t buffer[BUFFER_SIZE];
uint16_t bufferIndex = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);

  // Configure ADC
  analogWriteFreq(SAMPLE_RATE);  // Set ADC sampling frequency
}

void loop() {
  // Check if it's time to read a new sample
  if (micros() - lastSampleTime >= 1000000 / SAMPLE_RATE) {
    lastSampleTime = micros();

    // Read the analog input
    int16_t sample = analogRead(ADC_PIN);

    // Store the sample in the buffer
    buffer[bufferIndex] = sample;
    bufferIndex++;

    // If the buffer is full, send the data over serial
    if (bufferIndex == BUFFER_SIZE) {
      Serial.write((uint8_t *)buffer, sizeof(buffer));
      bufferIndex = 0;
    }
  }
}
