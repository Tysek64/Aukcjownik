import paho.mqtt.client as mqtt
from data.models import Auction, User
import time
import uuid

broker = "192.168.0.228"

client = None

def create_client(name):
    global client
    if client is None:
        client = mqtt.Client(f'{name}_{uuid.uuid4()}')
    else:
        raise AssertionError('client already created')

def connect_to_broker(topics, message_callback):
    global client
    if client is None:
        raise AssertionError('client not initialised')

    client.on_message = message_callback
    client.connect(broker, 1883)

    client.loop_start()
    for topic in topics:
        client.subscribe(topic)

def disconnect_from_broker():
    global client
    if client is None:
        raise AssertionError('client not initialised')

    client.loop_stop()
    client.disconnect()

def publish_message(topic, contents):
    global client
    if client is None:
        raise AssertionError('client not initialised')

    client.publish(topic, contents)
