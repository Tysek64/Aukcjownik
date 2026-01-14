#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time

# The broker name or IP address.
broker = "localhost"
# broker = "127.0.0.1"
# broker = "10.0.0.1"

users = {
    "981114580761": "Biała karta",
    "967700709850": "Krzychu",
    "769558007531": "Janas"
}

auction_state = {
    "current_price": 100,
    "current_bidder": None
}

client = mqtt.Client()

def process_message(client, userdata, message):
    message_decoded = (str(message.payload.decode("utf-8"))).split('/')

    if message.topic == 'auction/bid':
        auction_state['current_price'] = int(message_decoded[0])
    else:
        card_number = message_decoded[0]

        print(f"Card: {card_number}")
        if card_number in users.keys():
            print(f'User {users[card_number]} checked in')
            auction_state["current_bidder"] = users[card_number]
            auction_state["current_price"] += 10
            client.publish('auction/response/price', f'{auction_state["current_price"]}')
            client.publish('auction/response/bidder', f'{auction_state["current_bidder"]}')


def connect_to_broker():
    client.connect(broker)
    client.on_message = process_message

    client.loop_start()
    client.subscribe('card/data')
    client.subscribe('auction/bid')


def disconnect_from_broker():
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    connect_to_broker()

    while 1:
        pass

    disconnect_from_broker()
