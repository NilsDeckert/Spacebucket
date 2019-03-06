import paho.mqtt.publish as publish
import time
import datetime
import random

MQTT_SERVER = "192.168.178.66"
MQTT_PATH = "test_channel"

while True:

        publish.single(MQTT_PATH, random.randint(1,10), hostname=MQTT_SERVER)
        time.sleep(15)
