#!/usr/bin/env python3

# pylint: disable=no-member

import time
import datetime
import RPi.GPIO as GPIO
from config import * # pylint: disable=unused-wildcard-import
from mfrc522 import MFRC522
import neopixel
import board
import paho.mqtt.client as mqtt
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as libOled
import threading

terminal_id = "T0"
broker = "localhost"
#broker = "localhost"

client = mqtt.Client()

lastCard = 0
lastBuzzer = datetime.datetime.now() - datetime.timedelta(seconds=2)


auction_state = {
    "current_price": 100,
    "current_bidder": None
}

current_bid = auction_state['current_price']

def buzzer():
    global lastBuzzer
    #GPIO.output(buzzerPin, (datetime.datetime.now() - lastBuzzer) >= datetime.timedelta(seconds=0.5))  # pylint: disable=no-member

def rfidRead():
    global lastCard
    global lastBuzzer
    MIFAREReader = MFRC522()
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    if status == MIFAREReader.MI_OK:
        (status, uid) = MIFAREReader.MFRC522_Anticoll()
        if status == MIFAREReader.MI_OK:
            num = 0
            for i in range(0, len(uid)):
                num += uid[i] << (i*8)
            if lastCard != num:
                print(f"Card read UID: {uid} > {num}")
                print(f"Time: {datetime.datetime.now()}")
                client.publish('auction/bid', f'{current_bid}')
                client.publish('card/data', f'{num}')
                pixels.fill((0, 255, 0))
                pixels.show()
                lastBuzzer = datetime.datetime.now()
                lastCard = num
    else:
        lastCard = 0
        pixels.fill((255,0,0))
        pixels.show()

def process_message(client, userdata, message):
    global auction_state, current_bid
    message_decoded = (str(message.payload.decode("utf-8"))).split('/')
    if message.topic == 'auction/response/price':
        auction_state["current_price"] = int(message_decoded[0])
        current_bid = auction_state['current_price'] + 10
    elif message.topic == 'auction/response/bidder':
        auction_state["current_bidder"] = message_decoded[0]
        print(f'Current auction state: {auction_state["current_bidder"]} is bidding for ${auction_state["current_price"]}')
        oledDisplay(disp)
    #print(f"{message_decoded[0]} ")

def connect_to_broker():
    client.connect(broker)

    client.on_message = process_message

    client.loop_start()
    client.subscribe('card/response')
    client.subscribe('auction/response/+')

def disconnect_from_broker():
    client.loop_stop()
    client.disconnect()

def encEvent(_):
    global current_bid
    if GPIO.input(encoderRight):
        #encoder rotated left
        current_bid = max(auction_state['current_price'] + 10, current_bid - 10)
    else:
        #encoder rotated right
        current_bid += 10
    print(f'Current bid: {current_bid}')
        
def initDisplay():
    disp = libOled.SSD1331()
    disp.Init()
    disp.clear()

    return disp

def oledDisplay(disp):
    while (1):
        image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
        draw = ImageDraw.Draw(image1) 

        font = ImageFont.truetype('./lib/oled/Font.ttf', 9)
        
        draw.text((0,0), f'Bidder: {auction_state["current_bidder"]}, bid: {auction_state["current_price"]}', font=font, fill='BLACK')
        draw.text((0,20), f'Your bid: {current_bid}', font=font, fill='BLACK')
        disp.ShowImage(image1, 0, 0)

        time.sleep(2)

if __name__ == "__main__":
    global disp
    disp = initDisplay()
    displayThread = threading.Thread(target=oledDisplay, args=(disp,))
    displayThread.start()
    GPIO.add_event_detect(encoderLeft, GPIO.FALLING, callback=encEvent, bouncetime=50)
    connect_to_broker()
    pixels = neopixel.NeoPixel(
        board.D18, 8, brightness=1.0/32, auto_write=False)
    while 1:
        rfidRead()
        buzzer()
    disconnect_from_broker()
    GPIO.cleanup() # pylint: disable=no-member
