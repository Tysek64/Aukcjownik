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
    global auction_state
    message_decoded = (str(message.payload.decode("utf-8"))).split('/')
    if message.topic == 'auction/response/price':
        auction_state["current_price"] = int(message_decoded[0])
    elif message.topic == 'auction/response/bidder':
        auction_state["current_bidder"] = message_decoded[0]
    
    print(f'Current auction state: {auction_state["current_bidder"]} is bidding for ${auction_state["current_price"]}')

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
    print(current_bid)
        
if __name__ == "__main__":
    GPIO.add_event_detect(encoderLeft, GPIO.FALLING, callback=encEvent, bouncetime=50)
    connect_to_broker()
    pixels = neopixel.NeoPixel(
        board.D18, 8, brightness=1.0/32, auto_write=False)
    while 1:
        rfidRead()
        buzzer()
    disconnect_from_broker()
    GPIO.cleanup() # pylint: disable=no-member
