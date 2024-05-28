#include <Arduino.h>
#include <driver/i2s.h>
#include <esp_adc_cal.h>

#define I2S_SAMPLE_RATE 44100
#define I2S_BUFFER_SIZE 1024
#define SERIAL_BAUD_RATE 115200

// ADC configuration
#define ADC_CHANNEL ADC1_CHANNEL_7
#define ADC_ATTEN ADC_ATTEN_DB_11
#define ADC_WIDTH ADC_WIDTH_BIT_12

// ADC calibration
#define DEFAULT_VREF 1100
esp_adc_cal_characteristics_t *adc_chars;

// I2S configuration
i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_ADC_BUILT_IN),
    .sample_rate = I2S_SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S_MSB,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 2,
    .dma_buf_len = I2S_BUFFER_SIZE,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
};

void setup() {
  // Initialize serial communication
  Serial.begin(SERIAL_BAUD_RATE);

  // Configure ADC
  adc1_config_width(ADC_WIDTH);
  adc1_config_channel_atten(ADC_CHANNEL, ADC_ATTEN);
  adc_chars = (esp_adc_cal_characteristics_t *)calloc(1, sizeof(esp_adc_cal_characteristics_t));
  esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN, ADC_WIDTH, DEFAULT_VREF, adc_chars);

  // Initialize I2S
  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_adc_mode(ADC_UNIT_1, ADC_CHANNEL);
  i2s_adc_enable(I2S_NUM_0);
}

void loop() {
  size_t bytes_read;
  int16_t i2s_buffer[I2S_BUFFER_SIZE];
  int16_t audio_sample;

  // Read data from I2S
  i2s_read(I2S_NUM_0, (void *)i2s_buffer, I2S_BUFFER_SIZE * sizeof(int16_t), &bytes_read, portMAX_DELAY);

  for (int i = 0; i < bytes_read / sizeof(int16_t); i++) {
    // Get the audio sample
    audio_sample = i2s_buffer[i];

    // Send the audio sample over serial
    Serial.write((uint8_t *)&audio_sample, sizeof(audio_sample));
  }
}
