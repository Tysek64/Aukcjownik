#!/usr/bin/env python3

from config import *
import board
import busio
import time
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as libOled

if __name__ == '__main__':
    disp = libOled.SSD1331()
    disp.Init()
    disp.clear()
    
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1) 

    font = ImageFont.truetype('./lib/oled/Font.ttf', 9)
    
    draw.text((40,0), f'5 '+chr(176)+'C', font=font, fill='BLACK')

    disp.ShowImage(image1, 0, 0)
    time.sleep(2)

    disp.clear()
    disp.reset()

    GPIO.cleanup()
