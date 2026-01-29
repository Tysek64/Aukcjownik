import RPi.GPIO as GPIO
import time
from config import * # pylint: disable=unused-wildcard-import
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as libOled
import threading

disp = None
font = None

semaphore = False
current_state = {
    'auction_name': '',
    'current_winner': '',
    'current_price': 0,
    'current_bid': 0,
    'remaining_time': 0
}

signal = False

def init_display():
    global disp
    global font

    if disp is not None:
        raise AssertionError('display already initialised')

    disp = libOled.SSD1331()
    disp.Init()
    disp.clear()

    font = ImageFont.truetype('./lib/oled/Font.ttf', 9)

def update_state(key, value):
    while semaphore:
        pass
    current_state[key] = value

def signal_change():
    global signal

    signal = True



def display_auction_advertisement():
    global disp
    global font
    global current_state
    global signal

    if disp is None:
        raise AssertionError('display not initialised')

    semaphore = True
    local_state = current_state
    semaphore = False

    while not signal:
        image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
        draw = ImageDraw.Draw(image1)
        
        if local_state['auction_name'] != '':
            draw.text((0,0), f'Waiting for auction', font=font, fill='BLACK')
            draw.text((10,10), f'to start', font=font, fill='BLACK')
            draw.text((0,20), f'Name: {local_state["auction_name"]}', font=font, fill='BLACK')
            draw.text((0,30), f'Start price: {local_state["current_price"]}', font=font, fill='BLACK')
            draw.text((0,40), f'Duration: {local_state["remaining_time"] * 60}s', font=font, fill='BLACK')
        
        disp.ShowImage(image1, 0, 0)
        time.sleep(1)

    signal = False



def display_auction_state():
    global disp
    global font
    global current_state
    global signal

    if disp is None:
        raise AssertionError('display not initialised')

    semaphore = True
    local_state = current_state
    semaphore = False

    while not signal:
        image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
        draw = ImageDraw.Draw(image1)
        
        draw.text((0,0), f'Bidder: {local_state["current_winner"]}', font=font, fill='BLACK')
        draw.text((0,10), f'Bid: {local_state["current_price"]}', font=font, fill='BLACK')
        draw.text((0,20), f'Your bid: {local_state["current_bid"]}', font=font, fill='BLACK')
        draw.text((0,30), f'Remaining time: {local_state["remaining_time"]}s', font=font, fill='BLACK')
        disp.ShowImage(image1, 0, 0)
        time.sleep(1)

    signal = False



def display_auction_result():
    global disp
    global font
    global current_state
    global signal

    if disp is None:
        raise AssertionError('display not initialised')

    semaphore = True
    local_state = current_state
    semaphore = False

    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    
    draw.text((0,0), f'The winner is', font=font, fill='BLACK')
    draw.text((0,10), f'{local_state["current_winner"]}!', font=font, fill='BLACK')
    draw.text((0,20), f'For: {local_state["current_price"]}', font=font, fill='BLACK')
    draw.text((0,30), f'Congratulations!', font=font, fill='BLACK')
    disp.ShowImage(image1, 0, 0)

    signal = False