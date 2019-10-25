#!/usr/bin/env python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import Adafruit_DHT
import argparse
import threading
import time
import datetime
import pw
import sys

MQTT_SERVER = "192.168.178.67"
mydb = pw.login
mycursor = mydb.cursor()
DHTSensor = Adafruit_DHT.DHT11
GPIO.setmode(GPIO.BCM)
channel = 21
GPIO.setup(channel, GPIO.IN)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO_Pin = 23
stopthread = 0

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="Toggle debug output and additional commands", action="store_true")
args = parser.parse_args()
debug = args.debug

################### Welcome Message ###################
print("-----------------------------------------------------------------")
print("                    Publisher program started                    ")
print("-----------------------------------------------------------------")
print("")

################################################

try:
    mycursor.execute("SELECT * FROM settings")
    records = mycursor.fetchall()

    for row in records:
#       print("Id = ", row[0], )
       print("Name:           ", row[1])
       print("setHumidity:    ", row[5])
       print("setTemperature: ", row[6])
       print("LightFrom:      ", row[3])
       print("LightTo:        ", row[4], "\n")
       setHumidity = row[5]
       setTemperature = row[6]
       LightFrom = row[3]
       LightTo = row[4]
       print("Current time:    " + datetime.datetime.now().strftime('%H:%M:%S'))
except Error as e:
    print ("Error while connecting to MySQL", e)
finally:
    #closing database connection.
    if(mydb.is_connected()):
        mycursor.close()
        print("MySQL connection is closed")
################################################

print("|------------|------------------------|-----------|")

def callback(channel):
    if GPIO.input(channel):
        print("no water detected")
    else:
        print("water detected")

def push():
    try:
        global stopthread
        date = datetime.datetime.now().strftime('%d.%m.%Y')
        timeNow = datetime.datetime.now().strftime('%H:%M:%S')
        Humidity, Temperature = Adafruit_DHT.read_retry(DHTSensor, GPIO_Pin)
        publish.single("tmp_humidity", Humidity, hostname=MQTT_SERVER)
        print("| {} | humidity sent          |   {}%   |".format(date, Humidity))
        print("|------------|------------------------|-----------|")
        t1 = threading.Timer(900, push, args=[])
        t1.start()
        if stopthread is 1:
    #        _stop_event.set()
            t1.cancel()
            t1.join()
            stopthread = 0
        return
    except (KeyboardInterrupt, SystemExit):
        t1.join()
        exit()
        #cleanup_stop_thread()
        sys.exit()

def push2():
    try:
        global stopthread
        timeNow = datetime.datetime.now().strftime('%H:%M:%S')
        Humidity, Temperature = Adafruit_DHT.read_retry(DHTSensor, GPIO_Pin)
        publish.single("tmp_temperature", int(Temperature), hostname=MQTT_SERVER)
        print("| {}   | temperature sent       |   {}°C  |".format(timeNow, Temperature))
        t2 = threading.Timer(900, push2, args=[])
        t2.start()
        if stopthread is 1:
    #        _stop_event.set()
            t2.cancel()
            t2.join()
            stopthread = 0
        return
    except (KeyboardInterrupt, SystemExit):
        t2.join()
        exit()
        #cleanup_stop_thread()
        sys.exit()
##Soil sensor
def callback(channel):
    if GPIO.input(channel):
        print("no water detected")
        publish.single("tmp_soil", "no water", hostname=MQTT_SERVER)
        print("message sent")
    else:
        publish.single("tmp_soil", "water", hostname=MQTT_SERVER)
        print("water detected")

GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(channel, callback)

##Water sensor
def button_callback(channel1):
    print("Button pressed!")

GPIO.add_event_detect(10, GPIO.RISING)
GPIO.add_event_callback(10, button_callback)

push()
print(">>> {} Setting up initial time delay".format(datetime.datetime.now().strftime('%H:%M:%S')))
time.sleep(450)
time.sleep(15) #450
print(">>> Done")
print("|------------|------------------------|-----------|")
push2()
while True:
    try:
        global stopthread
        command = input()
        print("Input: "+ " " + command)
        if command == "force measure":
            print("")
            print("|------------|------------------------|-----------|")
            date = datetime.datetime.now().strftime('%d.%m.%Y')
            timeNow = datetime.datetime.now().strftime('%H:%M:%S')
            Humidity, Temperature = Adafruit_DHT.read_retry(DHTSensor, GPIO_Pin)
            publish.single("tmp_humidity", Humidity, hostname=MQTT_SERVER)
            print("| {} | humidity sent          |   {}%   |".format(date, Humidity))
            time.sleep(1)
            publish.single("tmp_temperature", int(Temperature), hostname=MQTT_SERVER)
            print("| {}   | temperature sent       |   {}°C  |".format(timeNow, Temperature))
            print("|------------|------------------------|-----------|")

        elif command == "fanspeed":
            fan_speed = input("Fanspeed:")
            if fan_speed:
                print("Fanspeed: " + fan_speed)
                publish.single("fan_speed", int(fan_speed), hostname=MQTT_SERVER)
            try:
                fan_speed = int(fan_speed)
                if fan_speed:
                    print("Fanspeed: " + str(fan_speed))
                    publish.single("fan_speed", fan_speed, hostname=MQTT_SERVER)
            except ValueError:
                if fan_speed:
                    print("Input has to be a number")
            #print("|------------|------------------------|-----------|")

        elif command == "help":
            print("Available commands:")
            print("  >force measure")
            print("  >fanspeed")
            print("  >exit")

        elif command == "exit":
            #sys.exit()
            stopthread = 1
            cleanup_stop_thread()
            raise SystemExit(0)
    except:
        exit()
