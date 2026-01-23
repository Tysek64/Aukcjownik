import paho.mqtt.client as mqtt
from models import Auction, User
import time

broker = "192.168.0.228"

client = mqtt.Client("server")

def connect_to_broker(topics, message_callback):
    client.on_message = message_callback
    client.connect(broker, 1883)

    client.loop_start()
    for topic in topics:
        client.subscribe(topic)


def disconnect_from_broker():
    client.loop_stop()
    client.disconnect()
