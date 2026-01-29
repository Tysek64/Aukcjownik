import time
import json
import datetime
from utils.mqtt_utils import connect_to_broker, disconnect_from_broker, publish_message, create_client
from utils.data_utils import parse_input
from random import randint
import threading
import terminal.screen_handler as screen_handler
import terminal.rfid_handler as rfid_handler
import RPi.GPIO as GPIO
from config import *
import board

can_start = False
current_auction = None
current_min_bid = 0
current_bid = 0
'''
def rfidRead():
    time.sleep(1)
    num = parse_input(None, name='your card ID', type=int, predicates=[lambda v: v is not None])
    current_bid = parse_input(None, name=f'your bid value (minimum is {current_min_bid})', type=float, predicates=[lambda v: v is not None, lambda v: v >= current_min_bid])
    print(f'User with card {num} is bidding for {current_bid}')
    publish_message('auction/bid', json.dumps({'card_id': num, 'bid_value': current_bid}))
    '''

def send_bid(card_id):
    print(f'User with card {card_id} is bidding for {current_bid}')
    publish_message('auction/bid', json.dumps({'card_id': card_id, 'bid_value': current_bid}))

def process_message(client, userdata, message):
    global can_start
    global current_auction
    global current_min_bid
    global current_bid

    message_decoded = (str(message.payload.decode("utf-8"))).split('/')

    if message.topic == 'auction/advertisement':
        current_auction = json.loads(message_decoded[0])
        screen_handler.update_state('auction_name', current_auction['auction_name'])
        screen_handler.update_state('current_price', current_auction['start_price'])
        screen_handler.update_state('current_bid', current_auction['start_price'])
        screen_handler.update_state('remaining_time', current_auction['end_time'])
        print(f'Received advertisement for {current_auction["auction_name"]}')

    elif message.topic == 'auction/start':
        can_start = True

    elif message.topic == 'auction/update':
        auction_update = json.loads(message_decoded[0])
        current_min_bid = auction_update['bid_value'] + current_auction['min_difference']
        current_bid = current_min_bid
        screen_handler.update_state('current_winner', auction_update['bidder'])
        screen_handler.update_state('current_price', auction_update['bid_value'])
        screen_handler.update_state('current_bid', current_min_bid)
        print(f'Current top bidder is {auction_update["bidder"]} for {auction_update["bid_value"]}\n')

    elif message.topic == 'auction/time':
        screen_handler.update_state('remaining_time', message_decoded[0])
        print(f'Remaining time until end is {message_decoded[0]}s')

    elif message.topic == 'auction/end':
        winner_details = json.loads(message_decoded[0])
        can_start = False
        print(f'=== AUCTION FOR {current_auction["auction_name"]} HAS ENDED ===')
        print(f'The winner is {winner_details["bidder"]} for {winner_details["bid_value"]}\nCongratulations!')

def encEvent(_):
    global current_bid
    if GPIO.input(encoderRight):
        #encoder rotated left
        current_bid = max(current_min_bid, current_bid - current_auction['min_difference'])
    else:
        #encoder rotated right
        current_bid += current_auction['min_difference']
    print(f'Current bid: {current_bid}')
    screen_handler.update_state('current_bid', current_bid)
        
if __name__ == "__main__":
    print("starting terminal...")
    screen_handler.init_display()
    rfid_handler.register_callback(send_bid)
    rfid_handler.init_rfid()
    create_client('terminal')
    connect_to_broker(['auction/advertisement', 'auction/start', 'auction/update', 'auction/time', 'auction/end'], process_message)
    
    GPIO.add_event_detect(encoderLeft, GPIO.FALLING, callback=encEvent, bouncetime=50)

    screen_thread = threading.Thread(target=screen_handler.display_auction_advertisement)
    screen_thread.start()

    # await auction start
    while not can_start or current_auction is None:
        pass

    screen_handler.signal_change()
    screen_thread.join()

    print(f'=== AUCTION FOR {current_auction["auction_name"]} HAS STARTED ===')
    current_min_bid = current_auction['start_price']
    current_bid = current_min_bid

    screen_thread = threading.Thread(target=screen_handler.display_auction_state)
    screen_thread.start()

    # once the auction has started
    # await bids
    while can_start:
        rfid_handler.rfid_read()

    screen_handler.signal_change()

    screen_thread.join()

    screen_thread = threading.Thread(target=screen_handler.display_auction_result)
    screen_thread.start()
    disconnect_from_broker()
    screen_thread.join()
