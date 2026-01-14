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

client = mqtt.Client()

lastCard = 0
lastBuzzer = datetime.datetime.now() - datetime.timedelta(seconds=2)

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
    message_decoded = (str(message.payload.decode("utf-8"))).split('/')

   
    print(f"{message_decoded[0]} ")

def connect_to_broker():
    client.connect(broker)

    client.on_message = process_message

    client.loop_start()
    client.subscribe('card/response')

def disconnect_from_broker():
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    connect_to_broker()
    pixels = neopixel.NeoPixel(
        board.D18, 8, brightness=1.0/32, auto_write=False)
    while 1:
        rfidRead()
        buzzer()
    disconnect_from_broker()
    GPIO.cleanup() # pylint: disable=no-member
