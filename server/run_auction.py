import datetime
import json
import time
import threading
from utils.mqtt_utils import connect_to_broker, disconnect_from_broker, create_client, publish_message
from utils.data_utils import parse_input
from utils.db_utils import db_get_user
from data.models import Auction

can_start = False
current_auction = None
current_top_bidder = None
current_top_bid = None

def run_auction(auction_name=None, start_price=None, end_time=None, min_difference=None):
    global can_start
    global current_auction
    global current_top_bidder
    global current_top_bid

    auction_name = parse_input(
        auction_name, 
        name='auction name', 
        predicates=[lambda v: v is not None, lambda v: len(v) > 0]
    )
    start_price = parse_input(
        start_price, 
        name='starting price', 
        type=float, 
        predicates=[lambda v: v is not None, lambda v: v >= 0]
    )
    end_time = parse_input(
        end_time, 
        name='time until auction end in minutes',
        type=int,
        predicates=[lambda v: v is not None, lambda v: v > 0]
    )
    min_difference = parse_input(
        min_difference,
        name='minimal difference between bids',
        type=float,
        predicates=[lambda v: v is not None, lambda v: v > 0]
    )

    current_auction = Auction(
        auction_name=auction_name, 
        start_price=start_price, 
        end_time=end_time, 
        min_difference=min_difference
    )
    current_top_bid = start_price - 1

    create_client('server')
    connect_to_broker(['auction/bid'], process_message)

    advertise_thread = threading.Thread(target=advertise_auction)
    advertise_thread.start()

    input_thread = threading.Thread(target=await_start_input)
    input_thread.start()

    input_thread.join()
    advertise_thread.join()

    publish_message('auction/start', json.dumps(current_auction.__dict__))
    print(f'=== STARTING AUCTION FOR {current_auction.auction_name} ===')

    # await bids
    # should check if time is over for auction
    time.sleep(60 * end_time)
    publish_message('auction/end', '')

    print(f'=== ENDING AUCTION FOR {current_auction.auction_name} ===')
    print(f'The winner is {current_top_bidder} for {current_top_bid}!\nCongratulations!')

    disconnect_from_broker()

def process_message(client, userdata, message):
    global current_auction
    global current_top_bidder
    global current_top_bid
    global can_start

    if can_start:
        message_topic = message.topic.split('/')
        message_decoded = str(message.payload.decode("utf-8")).split('/')

        # zakladamy, ze temat jest poprawny (auction/bid)
        bid_info = json.loads(message_decoded[0])

        bidder = db_get_user(card_id=bid_info['card_id'])
        if bidder is not None:
            print(f'User {bidder.username} with card {bid_info["card_id"]} wants to bid for {bid_info["bid_value"]}')
            if bid_info['bid_value'] > current_top_bid:
                current_top_bid = bid_info['bid_value']
                current_top_bidder = bidder.username

                print(f'Current bid is {bid_info["bid_value"]}\n')
                publish_message('auction/update', json.dumps({'bidder': bidder.username, 'bid_value': bid_info['bid_value']}))
            else:
                print(f'However, the current top bid is {current_top_bid} from {current_top_bidder}\n')
        else:
            print(f'Unknown user with card {card_number} checked in!')

def advertise_auction():
    global current_auction
    global can_start
    while not can_start:
        publish_message('auction/advertisement', json.dumps(current_auction.__dict__))
        print(f'Advertisement sent for {current_auction.auction_name}...')
        time.sleep(1)

def await_start_input():
    global can_start
    command = ''
    while command != 's':
        command = input("Type 's' to start auction ")
    can_start = True
