import paho.mqtt.publish as publish     #Needed for mqtt
import time                             #Needed for 'cooldown'
import random                           #Only needed for this example to generate random numbers, not needed in actual project

MQTT_SERVER = "192.168.178.66"          #Local IP-Address of the Raspberry Pi 2
MQTT_PATH = "test_channel"              #Channel the data is being sent in

while True:                             #Infinite Loop

        publish.single(MQTT_PATH, random.randint(1,10), hostname=MQTT_SERVER)   #Sending a random Number between 1 and 10
        time.sleep(15)                                                          #Waiting 15seconds until the next loop
