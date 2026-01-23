import time
import datetime
import paho.mqtt.client as mqtt
from random import randint

terminal_id = "T0"
broker = "192.168.0.228"

client = mqtt.Client("terminal")

lastCard = 0

auction_state = {
    "current_price": 100,
    "current_bidder": None
}

current_bid = auction_state['current_price']

def rfidRead():
    global lastCard
    global lastBuzzer
    if randint(0, 100000) == 5:
        (status, uid) = (0, [10, 10, 10, 10])
        num = 0
        for i in range(0, len(uid)):
            num += uid[i] << (i*8)
        if lastCard != num:
            print("publishing...")
            client.publish('auction/bid', f'{current_bid}')
            client.publish('card/data', f'{num}')
            lastCard = num
    else:
        lastCard = 0

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
    #encoder rotated left
    current_bid = max(auction_state['current_price'] + 10, current_bid - 10)
    #encoder rotated right
    current_bid += 10
    print(current_bid)
        
if __name__ == "__main__":
    print("starting terminal...")
    connect_to_broker()
    while 1:
        rfidRead()
    disconnect_from_broker()
    GPIO.cleanup() # pylint: disable=no-member
