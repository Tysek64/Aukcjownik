#!/usr/bin/env python3

from config import *
import board
import busio
import adafruit_bme280.advanced as bme280
import time
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as libOled

def initSensor():
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = bme280.Adafruit_BME280_I2C(i2c, 0x76)

    sensor.sea_level_pressure = 1013.25
    sensor.standby_period = bme280.STANDBY_TC_500
    sensor.iir_filter = bme280.IIR_FILTER_X16
    sensor.overscan_pressure = bme280.OVERSCAN_X16
    sensor.overscan_humidity = bme280.OVERSCAN_X1
    sensor.overscan_temperature = bme280.OVERSCAN_X2

    return sensor

def initDisplay():
    disp = libOled.SSD1331()
    disp.Init()
    disp.clear()

    return disp

def oledDisplay(disp, sensor):
    image1 = Image.open('temp_res.png')
    draw = ImageDraw.Draw(image1) 

    font = ImageFont.truetype('./lib/oled/Font.ttf', 9)
    
    draw.text((40,0), f'{sensor.temperature:0.1f} '+chr(176)+'C', font=font, fill='BLACK')
    draw.text((40,17), f'{sensor.humidity:0.1f} %', font=font, fill='BLACK')
    draw.text((40,33), f'{sensor.pressure:0.1f} hPa', font=font, fill='BLACK')
    draw.text((40,49),f'{sensor.altitude:0.2f} m', font=font, fill='BLACK')

    disp.ShowImage(image1, 0, 0)

def displayResults(sensor):
    print(f'Temperature:\t\t{sensor.temperature:0.1f} '+chr(176)+'C')
    print(f'Humidity:\t\t{sensor.humidity:0.1f} %')
    print(f'Pressure:\t\t{sensor.pressure:0.1f} hPa')

    altitude = 44330 * (1 - ((sensor.pressure / sensor.sea_level_pressure) ** (1 / 5.225)))
    print(f'Altitude (built-in):\t{sensor.altitude:0.2f} meters')
    print(f'Altitude (calculated):\t{altitude:0.2f} meters')

    print(f'\033[6A')


if __name__ == '__main__':
    sensor = initSensor()
    disp = initDisplay()

    while 1:
        oledDisplay(disp, sensor)

    GPIO.cleanup()
