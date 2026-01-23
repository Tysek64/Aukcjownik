import time
import json
import datetime
from utils.mqtt_utils import connect_to_broker, disconnect_from_broker, publish_message, create_client
from random import randint

can_start = False
current_auction = None
current_min_bid = 0

def rfidRead():
    if randint(0, 10000) == 5:
        (status, uid) = (0, [10, 0, 0, 0])
        num = 0
        for i in range(0, len(uid)):
            num += uid[i] << (i*8)
        print(f'User with card {num} is bidding for {current_min_bid}')
        publish_message('auction/bid', json.dumps({'card_id': num, 'bid_value': current_min_bid}))

def process_message(client, userdata, message):
    global can_start
    global current_auction
    global current_min_bid
    message_decoded = (str(message.payload.decode("utf-8"))).split('/')

    if message.topic == 'auction/advertisement':
        current_auction = json.loads(message_decoded[0])
        print(f'Received advertisement for {current_auction["auction_name"]}')
    if message.topic == 'auction/start':
        can_start = True
    elif message.topic == 'auction/update':
        auction_update = json.loads(message_decoded[0])

        print(f'Current top bidder is {auction_update["bidder"]} for {auction_update["bid_value"]}\n')
        current_min_bid = auction_update['bid_value'] + current_auction['min_difference']
    elif message.topic == 'auction/end':
        can_start = False

def encEvent(_):
    global current_bid
    # encoder rotated left
    current_bid = max(current_auction['current_price'] + 10, current_bid - 10)
    # encoder rotated right
    current_bid += 10
    print(current_bid)
        
if __name__ == "__main__":
    print("starting terminal...")
    create_client('terminal')
    connect_to_broker(['auction/advertisement', 'auction/start', 'auction/update', 'auction/end'], process_message)

    # await auction start
    while not can_start or current_auction is None:
        pass

    print(f'=== AUCTION FOR {current_auction["auction_name"]} HAS STARTED ===')
    current_min_bid = current_auction['start_price']

    # once the auction has started
    # await bids
    while can_start:
        rfidRead()

    print(f'=== AUCTION FOR {current_auction["auction_name"]} HAS ENDED ===')

    disconnect_from_broker()
