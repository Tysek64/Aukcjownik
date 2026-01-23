import datetime
from mqtt_utils import connect_to_broker, disconnect_from_broker
from data_utils import parse_input

def run_auction(auction_name=None, start_price=None, end_time=None, min_difference=None):
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

    print(f'=== STARTING AUCTION FOR {auction_name} ===')

    connect_to_broker([], process_message)

    while True:
        pass

    disconnect_from_broker()

def process_message(client, userdata, message):
    message_decoded = (str(message.payload.decode("utf-8"))).split('/')

    if message.topic == 'auction/bid':
        auction_state['current_price'] = int(message_decoded[0])
    else:
        card_number = message_decoded[0]

        print(f"Card: {card_number}")
        auction_state["current_bidder"] = users[card_number]
        client.publish('auction/response/price', f'{auction_state["current_price"]}')
        client.publish('auction/response/bidder', f'{auction_state["current_bidder"]}')
