from mfrc522 import MFRC522
from config import *
import neopixel
import board

pixels = None
MIFAREReader = None

lastCard = 0
callback = None

streak = 0

def init_rfid():
    global pixels
    global MIFAREReader

    pixels = neopixel.NeoPixel(
            board.D18, 8, brightness=1.0/32, auto_write=False)
    MIFAREReader = MFRC522()

def register_callback(_callback):
    global callback

    callback = _callback

def rfid_read():
    global callback
    global lastCard
    global pixels
    global MIFAREReader
    global streak

    if callback is None:
        raise AssertionError("no callback registered")

    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    if status == MIFAREReader.MI_OK:
        streak = 0
        (status, uid) = MIFAREReader.MFRC522_Anticoll()
        if status == MIFAREReader.MI_OK:
            num = 0
            for i in range(0, len(uid)):
                num += uid[i] << (i*8)
            if lastCard != num:
                callback(num)
                lastCard = num
                pixels.fill((0, 255, 0))
                pixels.show()
    else:
        if streak < 2:
            streak += 1
        else:
            lastCard = 0
            pixels.fill((255,0,0))
            pixels.show()