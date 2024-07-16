#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import smbus2
import time
import RPi.GPIO as GPIO


def power_on_sensor(sensor_pin):
    GPIO.output(sensor_pin, GPIO.HIGH)
    time.sleep(0.1)  # Sensörün güç alması için bekleyin

def power_off_sensor(sensor_pin):
    GPIO.output(sensor_pin, GPIO.LOW)
    time.sleep(0.1)  # Sensörün kapanması için bekleyin

def write_register(reg, value,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT):
    i2c.write_byte_data(TCS34725_ADDRESS, TCS34725_COMMAND_BIT | reg, value)

def read_register_16(reg,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT):
    data = i2c.read_i2c_block_data(TCS34725_ADDRESS, TCS34725_COMMAND_BIT | reg, 2)
    return data[1] << 8 | data[0]

def initialize_sensor(TCS34725_ENABLE,TCS34725_ATIME,TCS34725_CONTROL,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT):
    write_register(TCS34725_ENABLE, 0x01,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT)
    time.sleep(0.01)
    write_register(TCS34725_ENABLE, 0x03,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT)
    write_register(TCS34725_ATIME, 0xFF,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT)
    write_register(TCS34725_CONTROL, 0x00,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT)
    time.sleep(0.7)  # Entegrasyon zamanı

def read_color_ratio(TCS34725_CDATAL,TCS34725_RDATAL,TCS34725_GDATAL,TCS34725_BDATAL,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT):
    r = read_register_16(TCS34725_RDATAL,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT)
    g = read_register_16(TCS34725_GDATAL,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT)
    b = read_register_16(TCS34725_BDATAL,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT)
    c = read_register_16(TCS34725_CDATAL,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT)
    if c == 0:
        return 0
    else:
        return r / c


def color_start(color_log):
    
    # TCS34725 I2C adresi ve komut bitleri
    TCS34725_ADDRESS = 0x29
    TCS34725_COMMAND_BIT = 0x80

    # TCS34725 register adresleri
    TCS34725_ENABLE = 0x00
    TCS34725_ATIME = 0x01
    TCS34725_CONTROL = 0x0F
    TCS34725_CDATAL = 0x14
    TCS34725_RDATAL = 0x16
    TCS34725_GDATAL = 0x18
    TCS34725_BDATAL = 0x1A

    # I2C bus numarası (Jetson Nano'da genellikle I2C bus 0 kullanılır)
    I2C_BUS = 0

    # Sensör güç kontrol pinleri
    VCC1_PIN = 17  # GPIO 17
    VCC2_PIN = 27  # GPIO 27

    # I2C bus nesnesini oluştur
    i2c = smbus2.SMBus(I2C_BUS)

    # GPIO ayarları
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(VCC1_PIN, GPIO.OUT)
    GPIO.setup(VCC2_PIN, GPIO.OUT)

    
    # Kırmızı renk algılama eşiği
    RED_THRESHOLD = 0.46
    
    
    while True:
        # Sensör 1 için işlemler
        power_on_sensor(VCC1_PIN)
        initialize_sensor(TCS34725_ENABLE,TCS34725_ATIME,TCS34725_CONTROL,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT)
        red_ratio_1 = read_color_ratio(TCS34725_CDATAL,TCS34725_RDATAL,TCS34725_GDATAL,TCS34725_BDATAL,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT)
        power_off_sensor(VCC1_PIN)

        if red_ratio_1 > RED_THRESHOLD:
            print("Sensör 1: Kırmızı algılandı")
            color_log[0] = color_log[0] + 1

        else:
            print("Sensör 1: Kırmızı algılanmadı")

        # Sensör 2 için işlemler
        power_on_sensor(VCC2_PIN)
        initialize_sensor(TCS34725_ENABLE,TCS34725_ATIME,TCS34725_CONTROL,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT)
        red_ratio_2 = read_color_ratio(TCS34725_CDATAL,TCS34725_RDATAL,TCS34725_GDATAL,TCS34725_BDATAL,i2c,TCS34725_ADDRESS,TCS34725_COMMAND_BIT)
        power_off_sensor(VCC2_PIN)

        if red_ratio_2 > RED_THRESHOLD:
            print("Sensör 2: Kırmızı algılandı")
            color_log[0] = color_log[0] + 1

        else:
            print("Sensör 2: Kırmızı algılanmadı")

        time.sleep(1)

