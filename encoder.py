#!/usr/bin/env python3

from config import *
import board
import busio
import time
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as libOled

def initDisplay():
    disp = libOled.SSD1331()
    disp.Init()
    disp.clear()

    return disp

def oledDisplay(disp):
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1) 

    font = ImageFont.truetype('./lib/oled/Font.ttf', 9)
    
    draw.text((40,0), f'5 '+chr(176)+'C', font=font, fill='BLACK')

    disp.ShowImage(image1, 0, 0)

if __name__ == '__main__':
    disp = initDisplay()

    while 1:
        oledDisplay(disp)

    GPIO.cleanup()
